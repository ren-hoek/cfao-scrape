#!/bin/bash
sudo apt-get install wget
cd
wget https://repo.continuum.io/archive/Anaconda2-4.4.0-Linux-x86_64.sh
bash Anaconda3-4.4.0-Linux-x86_64.sh
rm Anaconda3-4.4.0-Linux-x86_64.sh
conda create --name cfao pip
source activate cfao
pip install -r requirements.txt
