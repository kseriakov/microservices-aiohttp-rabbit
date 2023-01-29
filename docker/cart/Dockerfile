FROM python:3.10.9-alpine3.17

ENV ROOT_FOLDER /var/www
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p ${ROOT_FOLDER}/cart

WORKDIR ${ROOT_FOLDER}
COPY req.txt ${ROOT_FOLDER}/cart

# build-base или alpine-sdk - для компляции приложений
RUN apk upgrade && apk update && \
    apk add build-base && \
    rm -rf /var/cache/apk/*

RUN pip install -r ${ROOT_FOLDER}/cart/req.txt

COPY ./docker/cart/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

CMD [ "/start" ]