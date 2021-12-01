#docker build -t abiam/rasa_nlu:v1 .
FROM rasa/rasa:2.8.6
USER root
RUN pip3 install spacy download es_core_news_sm
WORKDIR /app
COPY . .
#RUN rasa train
ENTRYPOINT ["rasa"]
CMD ["run","-m","models","--enable-api","--cors", "*","--debug"]

