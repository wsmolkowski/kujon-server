#!/usr/bin/env bash

APPDIR=/home/appuser/kujon.mobi/current
LOGDIR=/home/appuser/kujon.mobi/logs
export PYTHONPATH=$PYTHONPATH:$APPDIR

echo 'stopping services...'
sudo service nginx stop
sudo supervisorctl stop all
echo 'services stopped'

echo 'cloning code'
rm -rf $APPDIR
mkdir $APPDIR
cd $APPDIR
git clone ssh://github.com/kujonmobi/kujon-server.git .
ln -s /home/appuser/kujon.mobi/bower_components/ $APPDIR/web/static/

sudo chown -R appuser:appuser $APPDIR
sudo chmod +x $APPDIR/scripts/*
sudo chmod -R g+w $APPDIR
sudo chown -R appuser:appuser $LOGDIR
sudo chmod -R g+w $LOGDIR

echo 'starting services...'
sudo service nginx start
sudo supervisorctl start all
echo 'services started'
