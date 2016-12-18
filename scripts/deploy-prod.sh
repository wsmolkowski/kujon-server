#!/usr/bin/env bash

APPDIR=/home/appuser/prod.kujon.mobi/current
LOGDIR=/home/appuser/prod.kujon.mobi/log
export PYTHONPATH=$PYTHONPATH:$APPDIR

echo 'stopping services...'
# sudo service nginx stop
sudo supervisorctl stop kujon-prod:*
echo 'services stopped'

echo 'cloning code'
sudo rm -rf $APPDIR
mkdir $APPDIR
cd $APPDIR
git clone git@github.com:kujonmobi/kujon-server.git .
ln -s /home/appuser/prod.kujon.mobi/bower_components/ $APPDIR/web/static/

sudo chown -R appuser:appuser $APPDIR
sudo chmod +x $APPDIR/scripts/*
sudo chmod -R g+w $APPDIR
sudo chown -R appuser:appuser $LOGDIR
sudo chmod -R g+w $LOGDIR

echo 'starting services...'
#sudo service nginx start
sudo supervisorctl start kujon-prod:*
echo ""
sudo supervisorctl status kujon-prod:*

