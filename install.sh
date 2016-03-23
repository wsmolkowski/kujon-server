#!/bin/bash


LOGDIR="/var/log/kujon.mobi"
APPDIR="/opt/kujon.mobi"
ORIGUSER="$USER"


# Install any system packages (Ubuntu/Debian only) that are pre-requisites
if uname -a | grep "Debian\|Ubuntu"
then
    echo -e "\n\nInstalling required system packages . . ."
    sudo apt-get -y install gcc build-essential python-dev
    sudo apt-get -y install python-setuptools
    sudo apt-get -y install libffi-dev  	# For python bcrypt package
    sudo apt-get -y install nginx 		# For reverse http server
    sudo apt-get -y install git			# For code lookup
    sudo apt-get -y install npm			# For JS package management
    sudo apt-get -y install python-pip		# For Python package management
    # Install pip if required
    if ! which pip; then
        sudo easy_install-2.7 pip
    fi
fi


# Install all required Python packages
echo -e "\n\nInstalled required Python packages with pip . . ."
sudo -E pip install -r requirements.txt

# Create log directory and give $USER access to the folder
sudo mkdir -p $LOGDIR
sudo chown -hR $ORIGUSER $LOGDIR

# Create application directory and give $USER access to the folder
sudo mkdir -p $APPDIR
sudo chown -hR $ORIGUSER $APPDIR

# Copy config file over to $CONFDIR
#cp --no-clobber "config/cutthroat.conf" "${CONFDIR}/cutthroat.conf"
# For a quickstart; ideally the DB should be placed elsewhere
#cp --no-clobber "starter.db" "${DATADIR}/cutthroat.db"


echo -e "\n\nBootstrapping complete."

