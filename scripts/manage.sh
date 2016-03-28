#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

cd /home/appuser/kujon.mobi/current

case $1 in
        "start" )
                echo "start application services"
                service nginx start
                supervisorctl start all
                ;;
        "stop" )
                echo "stop application services"
                service nginx stop
                supervisorctl stop all
                ;;
        "restart" )
                echo "restart application services"
                service nginx stop
                supervisorctl stop all
                service nginx start
                supervisorctl start all
                ;;
        *)
                echo "need start|stop|restart"
                exit 1
esac
