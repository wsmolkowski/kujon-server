#!/usr/bin/env bash

USER="appuser"
APPDIR="/home/$USER/kujon.mobi"
LOGDIR=$APPDIR'/log/'


apt-get update

# Install any system packages (Ubuntu/Debian only) that are pre-requisites
if uname -a | grep "Debian\|Ubuntu"
then
    echo -e "\n\nInstalling required system packages . . ."
    apt-get -y install gcc build-essential python-dev
    apt-get -y install python-setuptools
    apt-get -y install libffi-dev     	# For python bcrypt package
    apt-get -y install nginx 		    # For reverse http server
    apt-get -y install npm		    	# For JS package management
    apt-get -y install git       		# For proper npm work
    apt-get -y install python-pip		# For Python package management
    apt-get -y install supervisor		# For Python package management
fi


# Install all required Python packages
echo -e "\n\nInstalled required Python packages with pip . . ."
pip install tornado
pip install pycurl
pip install pycrypto
pip install pymongo
pip install motor
pip install tornado

# Create log directory and give $USER access to the folder
mkdir -p $LOGDIR
chown -hR $ORIGUSER $LOGDIR

# Create application directory and give $USER access to the folder
mkdir -p $APPDIR
chown -hR $ORIGUSER $APPDIR

export PYTHONPATH=$PYTHONPATH:$APPDIR

npm install bower -g
ln -s /usr/bin/nodejs /usr/bin/node

cd /tmp

wget --header "Authorization: token 9310cac33743963aeda1010cd00844083e7c18b8" --header "Accept: application/vnd.github.v3.raw" --output-document=bower.sh https://raw.githubusercontent.com/kujonmobi/kujon-server/release-v1.0/scripts/bower.sh
chmod +x bower.sh

wget --header "Authorization: token 9310cac33743963aeda1010cd00844083e7c18b8" --header "Accept: application/vnd.github.v3.raw" --output-document=nginx.conf https://raw.githubusercontent.com/kujonmobi/kujon-server/release-v1.0/config/nginx.conf
wget --header "Authorization: token 9310cac33743963aeda1010cd00844083e7c18b8" --header "Accept: application/vnd.github.v3.raw" --output-document=supervisor.conf https://raw.githubusercontent.com/kujonmobi/kujon-server/release-v1.0/config/supervisor.conf
wget --header "Authorization: token 9310cac33743963aeda1010cd00844083e7c18b8" --header "Accept: application/vnd.github.v3.raw" --output-document=kujonmobi.supervisor https://raw.githubusercontent.com/kujonmobi/kujon-server/release-v1.0/config/kujonmobi.supervisor
wget --header "Authorization: token 9310cac33743963aeda1010cd00844083e7c18b8" --header "Accept: application/vnd.github.v3.raw" --output-document=bower.json https://raw.githubusercontent.com/kujonmobi/kujon-server/release-v1.0/config/bower.json

chow -R usr *

echo -e "\n\nBootstrapping complete."
