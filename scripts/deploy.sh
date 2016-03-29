#!/usr/bin/env bash

#git config --global user.name "kujonmobi"
#git config --global user.email "wsmo@protonmail.com"

APPDIR=/home/appuser/kujon.mobi/current
export PYTHONPATH=$PYTHONPATH:$APPDIR

echo 'stopping services...'
sudo service nginx stop
sudo supervisorctl stop all
echo 'services stopped'

echo 'cloning code'
rm -rf $APPDIR
git clone https://github.com/kujonmobi/kujon-server.git $APPDIR
chmod g+w -R $APPDIR
ln -s /home/appuser/kujon.mobi/bower_components/ $APPDIR/web/static/

echo 'starting services...'
sudo service nginx start
sudo supervisorctl start all
echo 'services started'

sudo chown -R appuser:appuser $APPDIR
