![](https://gitlab.mobileye.com/objs/osem-projects/dms/playground/giladk/dms-human/badges/dev/pipeline.svg)

# DMS - Human Detection
Welcome to the DMS project. See this project [Benchmark.](http://objs.gitpages.mobileye.com/osem-projects/dms/playground/giladk/dms-human/)

<img
src="https://gitlab.mobileye.com/uploads/-/system/project/avatar/31128/5097334.png?width=192"
alt="DMS"
height="300"/>

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
git clone git@gitlab.mobileye.com:objs/osem-projects/dms/playground/giladk/dms-human.git
cd dms-fd
poetry install
poetry shell
```

## Usage
Single image face detection:
```
dms-fd <path|url>
```

## Developing
Install [pre-commit](https://pre-commit.com/) hooks:
```
pre-commit install \
  --hook-type pre-commit \
  --hook-type pre-push
```
