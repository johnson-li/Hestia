#!/usr/bin/env bash

old_dir=`pwd`
cd "$(dirname "$0")"/..

containers=`docker ps -aq`
if [[ ! -z "$containers" ]]
then
    docker stop `docker ps -aq`
    docker rm `docker ps -aq`
fi
#images=`docker images -f dangling=true -q`
#if [[ ! -z "$images" ]]
#then
#    docker rmi `docker images -f dangling=true -q`
#fi
if [[ -z `docker network ls|grep hestianet` ]]
then
    docker network create --subnet=172.16.156.0/24 hestianet
fi
docker build --no-cache -t hestia:v1 -f dockerfiles/Dockerfile .
docker run --privileged -dP --net hestianet --ip 172.16.156.100 -e ROLE=balancer --name balancer1 hestia:v1
docker run --privileged -dP --net hestianet --ip 172.16.156.101 -e ROLE=server --name server11 hestia:v1
docker run --privileged -dP --net hestianet --ip 172.16.156.102 -e ROLE=server --name server12 hestia:v1

cd ${old_dir}



