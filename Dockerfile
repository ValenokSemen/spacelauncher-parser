# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:alpine as base

# If you prefer miniconda:
#FROM continuumio/miniconda3
FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN python3 -m pip install --prefix='/install' -r /requirements.txt

FROM base as runner
LABEL Name=spacelouncher Version=0.0.1
COPY --from=builder /install /usr/local
EXPOSE 5678
WORKDIR /app
ADD . /app

# Using pip:
# RUN python3 -m pip install -r requirements.txt
# CMD ["python3", "-m", "main.py", "debug"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "spacelouncher"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m spacelouncher"
