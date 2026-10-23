FROM python:3.12-slim-bookworm@sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt /opt/requirements.txt
RUN python -m pip install --only-binary=:all: -r /opt/requirements.txt
COPY vendor/appworld-src /opt/source/
RUN python -m pip install --no-deps --report /opt/appworld-install.json /opt/source/
RUN APPWORLD_ROOT=/opt/world HOME=/tmp python -m appworld.cli install
COPY prepare_data.py state_checker.py /probe/
RUN python /probe/prepare_data.py
COPY service.py /recovery/live_service.py
COPY client.py /recovery/client.py
USER 10001:10001
WORKDIR /work
ENV HOME=/work APPWORLD_ROOT=/work
CMD ["python", "/recovery/live_service.py"]
