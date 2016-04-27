#!/usr/bin/env bash

APPDIR=/home/appuser/kujon.mobi/current
export PYTHONPATH=$PYTHONPATH:$APPDIR

echo 'stopping services...'
sudo service nginx stop
sudo supervisorctl stop all
echo 'services stopped'

echo 'cloning code'
rm -rf $APPDIR
mkdir $APPDIR
cd $APPDIR
git clone https://github.com/kujonmobi/kujon-server.git .
ln -s /home/appuser/kujon.mobi/bower_components/ $APPDIR/web/static/

echo 'starting services...'
sudo service nginx start
sudo supervisorctl start all
echo 'services started'

sudo chown -R appuser:appuser $APPDIR
sudo chmod +x $APPDIR/scripts/deploy.sh
sudo chmod +x $APPDIR/scripts/manage.sh
