FROM python:3
WORKDIR /usr/src/app
COPY ./web/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY .. .
RUN chmod +x ./web/docker-entrypoint.sh
CMD ["./web/docker-entrypoint.sh" ]
