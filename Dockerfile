FROM python:3.8-slim

COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

WORKDIR /home/gltg-bmp

ENTRYPOINT ["./manage"]
