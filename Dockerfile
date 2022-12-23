FROM python:3.10.4-slim-buster
RUN apt update && apt upgrade -y
RUN apt-get -y install git
RUN apt-get install -y wget python3-pip curl bash neofetch ffmpeg software-properties-common
COPY requirements.txt .
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
COPY . .
RUN pip3 install wheel
RUN pip3 install --no-cache-dir -U -r requirements.txt
COPY start /start
CMD ["/bin/bash", "/start"]
