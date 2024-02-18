![](https://gitlab.mobileye.com/objs/osem-projects/dms/playground/giladk/dms-human/badges/dev/pipeline.svg)

# DMS - MediaPipe
A MediaPipe wrapper.

![](https://gitlab.mobileye.com/uploads/-/system/project/avatar/31422/mediapipe.jpg)

## Prerequisite
Make sure you have the following installed:
- [Poetry](https://python-poetry.org/)
- [pre-commit](https://pre-commit.com/)

- You need access to Artifactory:
  - Go to [Artifactory](https://artifactory.sddc.mobileye.com/ui/repos/tree/General/objs-dms-pypi-prod-local)
  - On the top right menu click on **Set Me Up**
  - Choose **pypi**
  - Select **objs-dms-pypi-prod-local**
  - On the **Upload** tab you can see your username and a generated password
  - Run `poetry config http-basic.me <username> <password>`

## Setup
```bash
git clone git@gitlab.mobileye.com:objs/osem-projects/dms/playground/giladk/mediapipe.git
cd dms-mediapipe
poetry install
poetry shell
```

## Usage
```
mp-face <in.mp4> <out.mp4>
mp-person <in.mp4> <out.mp4>
mp-fld <in.mp4> <out.mp4>
```

## Developing
Install [pre-commit](https://pre-commit.com/) hooks:
```
pre-commit install \
  --hook-type pre-commit \
  --hook-type pre-push
```
