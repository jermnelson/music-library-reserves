FROM ubuntu:14.04
MAINTAINER "Jeremy Nelson <jeremy.nelson@coloradocollege.edu>"

RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y gcc libc6-dev build-essential python3.4-dev python3-setuptools

RUN easy_install3 pip
