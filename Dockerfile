FROM python:3.9-slim-buster

WORKDIR /usr/src/app/web
COPY ./web/requirements.txt ./

RUN pip install -r requirements.txt  && rm -rf /root/.cache/pip
RUN python -m spacy download en_core_web_sm

COPY .. .
RUN chmod +x ./web/docker-entrypoint.sh
CMD ["./web/docker-entrypoint.sh" ]
