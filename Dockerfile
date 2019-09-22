FROM ubuntu:18.04

RUN apt-get update && \ 
	apt-get install -y python3 python3-pip && \
	pip3 install requests==2.18.4 \
                 discord==0.16.12 && \
	mkdir -p /opt/saltbot

ENV GIPHY_AUTH=${GIPHY_AUTH} \
	BOT_TOKEN=${BOT_TOKEN}

COPY goodnights.txt greetings.txt saltbot2.py auth /opt/saltbot/

WORKDIR /opt/saltbot

CMD python3 /opt/saltbot/saltbot2.py