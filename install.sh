#!/bin/bash
cd "$(dirname "${0}")"
declare -A OS_INFO;
OS_INFO[/etc/debian_version]="apt-get install"
OS_INFO[/etc/alpine-release]="apk --update add"
OS_INFO[/etc/centos-release]="yum install"
OS_INFO[/etc/fedora-release]="dnf install"
OS_INFO[/etc/arch-release]="pacman -S"
PYTHON_VER=$(python --version | sed -En "s/Python //p" | cut -c1-3)
PACKAGES=(aria2 git unzip wget)
BASE_DIR="$(pwd)"
MODELS_DIRECTORY=generator/gpt2/models
MODEL_VERSION=model_v5
MODEL_NAME=model-550
MODEL_TORRENT_URL="https://github.com/nickwalton/AIDungeon/files/3935881/model_v5.torrent.zip"
MODEL_TORRENT_BASENAME="$(basename "${MODEL_TORRENT_URL}")"

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
	echo "Creating directories."
	mkdir -p "${MODELS_DIRECTORY}"
	cd "${MODELS_DIRECTORY}"
	mkdir "${MODEL_VERSION}"
	wget "${MODEL_TORRENT_URL}"
	unzip "${MODEL_TORRENT_BASENAME}"
	which aria2c > /dev/null
	if [ $? == 0 ]; then
		echo -e "\n\n==========================================="
		echo "We are now starting to download the model."
		echo "It will take a while to get up to speed."
		echo "DHT errors are normal."
		echo -e "===========================================\n"
		aria2c \
			--max-connection-per-server 16 \
			--split 64 \
			--bt-max-peers 500 \
			--seed-time=0 \
			--summary-interval=15 \
			--disable-ipv6 \
			"${MODEL_TORRENT_BASENAME%.*}"
		echo "Download Complete!"
		pip_install
	else
		echo "aria2c isn't available in PATH."
		echo "Exiting."
		exit
	fi
}

reinstall () {
	echo "Deleting $MODELS_DIRECTORY"
	rm -rf ${MODELS_DIRECTORY}
	aid_install
}

if [[ -d "${MODELS_DIRECTORY}/${MODEL_VERSION}" ]]; then
	ANSWER="n"
	echo "AIDungeon2 is appears to be installed."
	echo "Would you like to reinstall?"
	echo "Warning, this will delete some files![y/N]"
	read ANSWER
	ANSWER=$(echo $ANSWER | tr '[:upper:]' '[:lower:]')
	case $ANSWER in
		"yes")
			reinstall;;
		"y")
			reinstall;;
		*)
			echo "Exiting program!"
			exit;;
	esac
fi

aid_install
