import json
from importlib.resources import files
from pathlib import Path
from typing import Any, Callable, Generator, Literal, TypeVar

import numpy as np
from cv2.typing import MatLike
from dms_util import bbox, img, vid

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

T = TypeVar("T")
Frame = MatLike
XYXY = tuple[int, int, int, int]
Task = Literal['person', 'face', 'fld']
Point = tuple[int, int]


def area(box):
    return box.width * box.height


def xyxy(box):
    x1 = box.origin_x
    y1 = box.origin_y
    x2 = x1 + box.width
    y2 = y1 + box.height

    return x1, y1, x2, y2


def asset2buffer(name: str):
    import dms_mediapipe
    return files(dms_mediapipe).joinpath(name).read_bytes()


class MediaPipe:
    def __init__(self, cache_dir='.media_pipe') -> None:
        self.version = 3
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.person_detector = vision.ObjectDetector.create_from_options(
            vision.ObjectDetectorOptions(
                max_results=10,
                running_mode=vision.RunningMode.IMAGE,
                base_options=mp.tasks.BaseOptions(
                    model_asset_buffer=asset2buffer('efficientdet.tflite'))))

        self.face_detector = vision.FaceDetector.create_from_options(
            vision.FaceDetectorOptions(
                running_mode=vision.RunningMode.IMAGE,
                base_options=mp.tasks.BaseOptions(
                    model_asset_buffer=asset2buffer('blaze_face_short_range.tflite'))))

        self.fld_detector = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                output_face_blendshapes=True,
                output_facial_transformation_matrixes=True,
                num_faces=1,
                base_options=python.BaseOptions(
                    model_asset_buffer=asset2buffer('face_landmarker_v2_with_blendshapes.task'))))

    def img_from_cv(self, frame: np.ndarray) -> mp.Image:
        return mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

    def img_from_file(self, path: str | Path) -> mp.Image:
        return mp.Image.create_from_file(path)

    def max_person_xyxy(self, frame: mp.Image) -> XYXY | None:
        detections = self.person_detector.detect(frame).detections

        humans = [
            d for d in detections if any([
                cat.category_name == 'person' and cat.score > 0.1
                for cat in d.categories])]

        if not humans:
            return None

        human = max(humans, key=lambda det: area(det.bounding_box))
        bbox = xyxy(human.bounding_box)

        return bbox

    def max_face_xyxy(self, frame: mp.Image) -> XYXY | None:
        faces = self.face_detector.detect(frame).detections
        if not faces:
            return None

        face = max(faces, key=lambda det: area(det.bounding_box))
        bbox = xyxy(face.bounding_box)

        return bbox

    def me58(self, frame: mp.Image):
        return [
            (int(lm.x * frame.width), int(lm.y * frame.height))
            for lm in self.fld_detector.detect(frame).face_landmarks[0]]

    def cash_json(self, path_mp4: Path, task: Task):
        return self.cache_dir / task / f'{path_mp4.stem}.json'

    def annotate(self, path_mp4: Path, cache_json: Path, annotator: Callable[[mp.Image], T]) -> Generator[tuple[MatLike, T], Any, Any]:
        cap = vid.open_video(path_mp4)
        frames = vid.read_frames_hwc(cap)

        if cache_json.exists():
            with open(cache_json) as f:
                annotations = json.load(f)
                if annotations['version'] == self.version:
                    frames = list(frames)
                    for frame, a in zip(
                            frames,
                            annotations['annotations']):
                        yield frame, a

                    return

        annotations = []
        cache_json.parent.mkdir(parents=True, exist_ok=True)

        for frame in frames:
            mp_frame = self.img_from_cv(frame)
            a = annotator(mp_frame)
            annotations.append(a)
            yield frame, a

        with open(cache_json, 'w') as f:
            json.dump({'version': self.version, 'annotations': annotations}, f)

    def face_xyxy(self, path_mp4: Path):
        yield from self.annotate(path_mp4, self.cash_json(path_mp4, 'face'), self.max_face_xyxy)

    def person_xyxy(self, path_mp4: Path):
        yield from self.annotate(path_mp4, self.cash_json(path_mp4, 'person'), self.max_person_xyxy)

    def fld(self, path_mp4: Path):
        yield from self.annotate(
            path_mp4,
            self.cash_json(path_mp4, 'fld'),
            self.me58)


def face(in_mp4: str | Path, out_mp4: str | Path):
    from tqdm import tqdm
    in_mp4 = Path(in_mp4)
    out_mp4 = Path(out_mp4)
    mp = MediaPipe()

    cap = vid.open_video(in_mp4)
    height = vid.frame_height(cap)
    width = vid.frame_width(cap)

    def frames():
        for frame, xyxy in tqdm(mp.face_xyxy(in_mp4)):
            frame = img.cv2pil(frame)

            if xyxy is not None:
                bbox.draw_bbox(frame, bbox.BBox.from_xyxy(xyxy))

            yield img.pil2cv(frame)

    vid.write_frames(
        frames(),
        out_mp4,
        width=width,
        height=height)


def person(in_mp4: str | Path, out_mp4: str | Path):
    from tqdm import tqdm
    in_mp4 = Path(in_mp4)
    out_mp4 = Path(out_mp4)
    mp = MediaPipe()

    cap = vid.open_video(in_mp4)
    height = vid.frame_height(cap)
    width = vid.frame_width(cap)

    def frames():
        for frame, xyxy in tqdm(mp.person_xyxy(in_mp4)):
            frame = img.cv2pil(frame)

            if xyxy is not None:
                bbox.draw_bbox(frame, bbox.BBox.from_xyxy(xyxy))

            yield img.pil2cv(frame)

    vid.write_frames(
        frames(),
        out_mp4,
        width=width,
        height=height)


def fld(in_mp4: str | Path, out_mp4: str | Path):
    import cv2
    from tqdm import tqdm
    in_mp4 = Path(in_mp4)
    out_mp4 = Path(out_mp4)
    mp = MediaPipe()

    cap = vid.open_video(in_mp4)
    height = vid.frame_height(cap)
    width = vid.frame_width(cap)

    def frames():
        for frame, landmarks in tqdm(mp.fld(in_mp4)):
            for x, y in landmarks:
                cv2.circle(
                    frame,
                    center=(x, y),
                    radius=5,
                    color=(0, 255, 0))

            yield frame

    vid.write_frames(
        frames(),
        out_mp4,
        width=width,
        height=height)


def fire_face():
    from fire import Fire
    Fire(face)


def fire_person():
    from fire import Fire
    Fire(person)


def fire_fld():
    from fire import Fire
    Fire(fld)
