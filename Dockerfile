FROM python:3.6.2
MAINTAINER furion <_@furion.me>

# add our code
COPY . /project_root

# install node.js
RUN apt-get update && \
    apt-get install -y nodejs npm &&\
    rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/nodejs /usr/bin/node

# compile the dependencies
WORKDIR /project_root/src/static
RUN npm install
#RUN npm install -g browserify
#RUN browserify -r eosjs > bundle.js

WORKDIR /project_root
RUN pip install -r requirements.txt

# RUN python mange.py db-create
ENV PRODUCTION yes
ENV IPFS_URL https://ipfs.view.ly
EXPOSE 5000
CMD ["gunicorn", "-w", "1", "-t", "60", "-b", "0.0.0.0:5000", "src.views:app"]
