FROM ubuntu:20.04
LABEL maintainer="Dakota Marshall <me@dakotamarshall.net>"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y
RUN apt install -y firefox sqlite python python3-pip wget

COPY ./* ./
RUN pip install -r requirements.txt

ENTRYPOINT ["./main.py"]