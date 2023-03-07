FROM python:3.12.0a5-slim
LABEL maintainer="Dakota Marshall <me@dakotamarshall.net>"
ENV TZ="America/New_York"

RUN mkdir /app
COPY ./* /app/
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 80

CMD [ "python", "./main.py" ]
