FROM python:3.7-slim

WORKDIR /home/bmp-api


COPY ./requirements.txt /home/bmp-api
COPY ./manage /home/bmp-api

RUN pip install -r requirements.txt

COPY ./api /home/bmp-api/api/
COPY ./swagger /home/bmp-api/swagger/
COPY ./app.py /home/bmp-api

RUN ls

ENV FLASK_APP=app.py

ENTRYPOINT [ "./manage" ]
CMD ["-d"]
