FROM python:3.9-slim

ENV CLOWDER_URL=$CLOWDER_URL

RUN apt-get -q update && apt-get -y upgrade

# install python packages
COPY ./requirements /tmp/requirements
RUN pip install -r /tmp/requirements/extractor.txt
RUN rm -r /tmp/requirements

WORKDIR /home/gltg-bmp/

CMD ["python", "-m", "extractor.practices_extractor"]
