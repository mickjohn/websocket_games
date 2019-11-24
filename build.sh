#!/bin/bash
set -e

if [ ! -d "virtualenv" ];then
  virtualenv -p python3.7 virtualenv
fi

source virtualenv/bin/activate
pip install -r requirements.txt
python build.py
