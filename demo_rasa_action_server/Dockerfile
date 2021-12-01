#docker build -t abiam/rasa_sdk:v1 .
FROM rasa/rasa:2.8.6
WORKDIR /app
USER root
COPY ./actions /app/actions
ENTRYPOINT ["rasa"]
CMD ["run","actions","--debug"]