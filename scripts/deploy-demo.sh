#!/usr/bin/env bash

APPDIR=/home/appuser/demo.kujon.mobi/current
LOGDIR=/home/appuser/demo.kujon.mobi/log
export PYTHONPATH=$PYTHONPATH:$APPDIR

echo 'stopping services...'
sudo supervisorctl stop kujon-demo:*

echo 'cloning code'
sudo rm -rf $APPDIR
mkdir $APPDIR
cd $APPDIR
git clone -b development git@github.com:kujonmobi/kujon-server.git .
ln -s /home/appuser/demo.kujon.mobi/bower_components/ $APPDIR/web/static/

sudo chown -R appuser:appuser $APPDIR
sudo chmod +x $APPDIR/scripts/*
sudo chmod -R g+w $APPDIR
sudo chown -R appuser:appuser $LOGDIR
sudo chmod -R g+w $LOGDIR


echo 'recreating usosinstances...'
cd $APPDIR
python3.5 ./scripts/dbutils.py -r -e demo

echo 'starting services...'
sudo supervisorctl start kujon-demo:*
echo ""
sudo supervisorctl status kujon-demo:*
