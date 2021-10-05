FROM python:3
WORKDIR /usr/src/app/web
COPY ./web/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY .. .
RUN chmod +x ./web/docker-entrypoint.sh
CMD ["./web/docker-entrypoint.sh" ]
