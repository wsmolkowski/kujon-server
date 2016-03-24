#!/usr/bin/env bash

LOGDIR="/var/log/kujon.mobi"
APPDIR="/opt/kujon.mobi"
ORIGUSER="$USER"


# Install any system packages (Ubuntu/Debian only) that are pre-requisites
if uname -a | grep "Debian\|Ubuntu"
then
    echo -e "\n\nInstalling required system packages . . ."
    apt-get -y install gcc build-essential python-dev
    apt-get -y install python-setuptools
    apt-get -y install libffi-dev  	# For python bcrypt package
    apt-get -y install nginx 		    # For reverse http server
    apt-get -y install npm		    	# For JS package management
    apt-get -y install python-pip		# For Python package management
    apt-get -y install curl    		#
    # Install pip if required
    if ! which pip; then
        easy_install pip
    fi
fi


# Install all required Python packages
echo -e "\n\nInstalled required Python packages with pip . . ."
-E pip install -r requirements.txt

# Create log directory and give $USER access to the folder
mkdir -p $LOGDIR
chown -hR $ORIGUSER $LOGDIR

# Create application directory and give $USER access to the folder
mkdir -p $APPDIR
chown -hR $ORIGUSER $APPDIR

export PYTHONPATH=$PYTHONPATH:/opt/kujon.mobi/current

npm install bower -g
ln -s /usr/bin/nodejs /usr/bin/node


echo -e "\n\nBootstrapping complete."
