#!/bin/bash

docker build -t alpha.view.ly .
docker tag alpha.view.ly furion/alpha.view.ly
docker push furion/alpha.view.ly
