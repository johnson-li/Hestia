#!/usr/bin/env bash

source ~/env

case ${ROLE} in
    "balancer")
        interface=`route |grep default| head -n1| tr -s ' '| cut -d' ' -f8`
        sudo -b LD_LIBRARY_PATH="$HOME/app/bin" ~/app/bin/balancer --mysql='35.228.52.213' --user='johnson' --password='welcOme0!' ${interface} 0.0.0.0 4433 ~/app/keys/server.key ~/app/keys/server.cert > $HOME/balancer.log 2>&1
        ;;
   "server")
        sudo -b LD_LIBRARY_PATH="$HOME/app/bin" ~/app/bin/server 0.0.0.0 4433 ~/app/keys/server.key ~/app/keys/server.cert > $HOME/server.log 2>&1
   ;;
esac
