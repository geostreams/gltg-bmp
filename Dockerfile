FROM python:3.9-slim

COPY ./api /home/gltg-bmp/api
COPY ./extractor /home/gltg-bmp/extractor
COPY ./requirements /home/gltg-bmp/requirements
COPY ./__init__.py /home/gltg-bmp/__init__.py
COPY ./data/assumptions.xlsx /home/gltg-bmp/data/assumptions.xlsx
COPY ./data/baselines.json /home/gltg-bmp/data/baselines.json
COPY ./data/boundaries.xlsx /home/gltg-bmp/data/boundaries.xslx

WORKDIR /home/gltg-bmp/

RUN pip install -U pip
RUN pip install -r /home/gltg-bmp/requirements/api.txt -r /home/gltg-bmp/requirements/extractor.txt
