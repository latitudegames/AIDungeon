#!/bin/bash
cd "$(dirname "${0}")"
BASE_DIR="$(pwd)"

declare -A OS_INFO;
OS_INFO[/etc/debian_version]="apt-get install"
OS_INFO[/etc/alpine-release]="apk --update add"
OS_INFO[/etc/centos-release]="yum install"
OS_INFO[/etc/fedora-release]="dnf install"
OS_INFO[/etc/arch-release]="pacman -S"
PYTHON_VER=$(python --version | sed -En "s/Python //p" | cut -c1-3)
PACKAGES=(aria2 git unzip wget)

pip_install () {
	if [ "$PYTHON_VER" != "3.6" ]; then 
		echo "One of the packages 'Tensorflow 1.15' only supports Python 3.6.x"
		echo "Your default Python installation is $PYTHON_VER.x."
		echo "You'll need to install Python 3.6 manually and then do"
		echo "pip install -r ./requirements.txt"
		echo "If you have 3.6 installed, please enter the full path of pip3.6."
		echo "Leave blank to exit the installation."
		read PIP36
	else
		PIP36=$(which pip)
		 
	fi
	if [[ ! -z "$PIP36" ]]; then
		echo "Installing Python packages."
		sudo ${PIP36} install --upgrade pip setuptools
		sudo ${PIP36} install -r $BASE_DIR/requirements.txt
	fi
	echo "Once everything is installed, play the game with 'python3.6 ./play.py'"
	exit
}

aid_install () {
	echo "Determining package manager."
	for f in ${!OS_INFO[@]}
	do
		if [[ -f $f ]]; then
			echo "Found $f."
			PACKAGE_MANAGER=${OS_INFO[$f]}
		fi
	done
	if [ -z "$PACKAGE_MANAGER" ]; then
		echo "You do not seem to be using a supported package manager."
		echo "Please make sure ${PACKAGES[@]} are installed then press [ENTER]"
		read NOT_USED
	else
		sudo ${PACKAGE_MANAGER} ${PACKAGES[@]}
	fi
		pip_install
	else
		echo "aria2c isn't available in PATH."
		echo "Exiting."
		exit
	fi
}

aid_install
