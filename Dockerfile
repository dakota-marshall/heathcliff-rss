FROM python:3
LABEL maintainer="Dakota Marshall <me@dakotamarshall.net>"
ENV TZ="America/New_York"

COPY ./* ./
RUN pip install -r requirements.txt

CMD [ "python", "./main.py" ]