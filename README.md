Editar Makefile

ccap=75 De acordo com sua GPU Nvidia RTX2060

ccap=86 De acordo com sua GPU Nvidia RTX3060

ccap=89 De acordo com sua GPU Nvidia RTX4090

ccap=120 De acordo com sua GPU Nvidia RTX5090

CXX = g++-9

CUDA = /usr/local/cuda-12.8 De acordo com sua instalação

CXXCUDA = /usr/bin/g++-9

NVCC = nvcc

sudo apt install python3-venv

python3 -m venv myenv

source myenv/bin/activate

sudo apt install g++-9 -y

sudo apt install build-essential -y

sudo apt install libssl-dev -y

sudo apt install libgmp-dev -y

pip install python-telegram-bot

pip install requests

pip install base58

make clean

make gpu=1 CCAP=86 all

./Rotor -g --gpui 0 --gpux 512,512 -m ADDRESSES --coin BTC --range 5CC295BB0000000000:5CC295BC0000000000 -i hash160_out.bin

./Rotor -g --gpui 0 --gpux 512,512 -m ADDRESS --coin BTC --range 8000000000000000:ffffffffffffffff -i 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU
