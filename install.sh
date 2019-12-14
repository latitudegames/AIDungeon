#!/usr/bin/env bash
set -e
cd "$(dirname "${0}")"
BASE_DIR="$(pwd)"
PACKAGES=(aria2 git unzip wget)

pip_install () {
	if [ ! -d "./venv" ]; then
		apt-get install python3-venv
		python3 -m venv ./venv
	fi
	source "${BASE_DIR}/venv/bin/activate"
	pip install --upgrade pip setuptools
	pip install -r "${BASE_DIR}/requirements.txt"
}

is_command() {
	command -v "${@}" > /dev/null
}

system_package_install() {
	PACKAGES=(aria2 git unzip wget)
	if is_command 'apt-get'; then
		sudo apt-get install ${PACKAGES[@]}
	elif is_command 'brew'; then
		brew install ${PACKAGES[@]}
	elif is_command 'yum'; then
		sudo yum install ${PACKAGES[@]}
	elif is_command 'dnf'; then
		sudo dnf install ${PACKAGES[@]}
	elif is_command 'packman'; then
		sudo packman -S ${PACKAGES[@]}
	elif is_command 'apk'; then
		sudo apk --update add ${PACKAGES[@]}
	else
		echo "You do not seem to be using a supported package manager."
		echo "Please make sure ${PACKAGES[@]} are installed then press [ENTER]"
		read NOT_USED
	fi
}

install_aid () {
	pip_install
	system_package_install
}

install_aid
