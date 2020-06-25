FROM ubuntu:18.04

RUN apt-get update && \ 
	apt-get install -y python3 python3-pip && \
	pip3 install requests==2.18.4 \
                 discord==0.16.12 && \
	mkdir -p /opt/saltbot

ARG GIPHY_AUTH
ARG BOT_TOKEN
ARG EMAIL_PASSWORD

ENV GIPHY_AUTH=${GIPHY_AUTH} \
	BOT_TOKEN=${BOT_TOKEN} \
	EMAIL_PASSWORD=${EMAIL_PASSWORD}

COPY saltbot2.py /opt/saltbot/
COPY lib /opt/saltbot/

WORKDIR /opt/saltbot

CMD python3 /opt/saltbot/saltbot2.py
