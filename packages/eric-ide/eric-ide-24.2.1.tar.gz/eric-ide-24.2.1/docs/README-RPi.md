# Readme for use on a Raspberry Pi 4

In order to use eric7 on a Raspberry Pi 4 computer a Linux distribution providing
`Qt6` and `PyQt6` packages need to be installed. This recipe was tested on
__Manjaro ARM__.

This requirement is there because up to now no `PyQt6` and `PyQt6-Qt6` (and the like)
wheels are available form ARM computers via the Python Packaging Index PyPI.

## 1. Step 1: Qt6 and PyQt6
Ensure the following `Qt6` and `PyQt6` packages are installed or install them.

- qt6-base
- qt6-charts
- qt6-doc
- qt6-imageformats
- qt6-multimedia
- qt6-serialport
- qt6-svg
- qt6-tools
- qt6-translations
- qt6-webchannel
- qt6-webengine
- python-pyqt6
- python-pyqt6-charts
- python-pyqt6-sip
- python-pyqt6-webengine
- python-qscintilla-qt6
- qscintilla-qt6


## 2. Step 2: Spell Checking
If spell checking is desired, ensure the following packages are installed.

- enchant
- python-enchant
- aspell
- any aspell language dictionary desired (suggested at least 'aspell-en')

## 3. Step 3: Prepare eric7 Installation
In order to install eric7 it is recommended to create a Python virtual environment in
order to isolate the eric7 execution environment as much as possible from the standard
installation. In order to create this environment execute the following in a terminal
window.

    python3 -m venv --system-site-packages eric7_env
    ~/eric7_env/bin/python3 -m pip install --upgrade pip

__Note:__ The switch `--system-site-packages` is necessary because there are no
PyQt6/Qt6 packages available for the AArch64 (ARM) platform. This necessitates
the use of the packages provided by the distribution.

## 4. Step 4: Install eric7 (eric-ide)
Install eric7 into the created Python virtual environment by following these steps.

    ~/eric7_env/bin/python3 -m pip install --prefer-binary eric-ide
    ~/eric7_env/bin/eric7_post_install
