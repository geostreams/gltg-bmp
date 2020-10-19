FROM python:3.7

ENV MAIN_SCRIPT="practices_extractor.py"

COPY . /home/clowder/
WORKDIR /home/clowder/

RUN if [ -e packages.apt ]; then \
                apt-get -q -q update \
                && xargs apt-get -y install --no-install-recommends < packages.apt \
                && rm -rf /var/lib/apt/lists/*; \
            fi

# install python packages
RUN if [ -e requirements.txt ]; then \
                pip install --no-cache-dir -r requirements.txt; \
            fi


RUN ls
CMD python "./${MAIN_SCRIPT}"
