# Dockerfile for Colorado College Music Library Reserves
FROM python:3.4.3
MAINTAINER Jeremy Nelson <jeremy.nelson@coloradocollege.edu>

# Environmental Variables
ENV RESERVES_HOME /opt/music-reserves
ENV NGINX_HOME /etc/nginx

# Updated Ubuntu and install Python 3 setuptools, nginx,
# and other other packages
RUN apt-get update \
  && apt-get install -y python3-setuptools \
  && apt-get install -y nginx \
  && apt-get install -y python3-pip

ADD . $RESERVES_HOME
WORKDIR $RESERVES_HOME
RUN cd $RESERVES_HOME  \
   && pip install -r requirements.txt 

EXPOSE 8000
EXPOSE 18760
CMD python app.py run
