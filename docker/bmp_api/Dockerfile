FROM python:3.9-slim

COPY ./requirements /tmp/requirements
RUN pip install -r /tmp/requirements/api.txt
RUN rm -r /tmp/requirements

WORKDIR /home/gltg-bmp

ENTRYPOINT ["python", "api/app.py"]
