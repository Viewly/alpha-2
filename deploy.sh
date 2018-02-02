#!/bin/bash

docker build -t alpha-2.web -f Dockerfile.web .
docker tag alpha-2.web furion/alpha-2:web
docker push furion/alpha-2:web

docker build -t alpha-2.worker -f Dockerfile.worker .
docker tag alpha-2.worker furion/alpha-2:worker
docker push furion/alpha-2:worker

docker build -t alpha-2.migrations -f Dockerfile.migrations .
docker tag alpha-2.migrations furion/alpha-2:migrations
docker push furion/alpha-2:migrations
