
build python12 on 210

https://wiki.crowncloud.net/?How_to_Install_Python_3_12_on_CentOS_Stream_8
https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz

wget https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz


tar -xf Python-3.12.2.tgz

cd Python-3.12.2

dnf install gcc openssl-devel bzip2-devel libffi-devel wget tar make

./configure --enable-optimizations


make -j $(nproc)
sudo make altinstall

sudo wget https://www.openssl.org/source/openssl-1.1.1l.tar.gz

sudo ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib

sudo make install


https://vishwakarmarohit.medium.com/installing-python3-with-openssl-1-1-1-a247c0d27317

cd openssl-1.1.1l
sudo ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib
sudo make
sudo make install

[centos@fu-yuan openssl-1.1.1l]$ openssl version
openssl: symbol lookup error: openssl: undefined symbol: EVP_md2, version OPENSSL_1_1_0

嘗試重開機

依照
https://medium.com/pythoneers/installing-python-3-on-amazon-linux-with-openssl-and-pip-dependencies-2e9c76b91018

嘗試安裝openssl11

 which openssl11
/usr/bin/which: no openssl11 in (/usr/local/cuda/bin:/home/centos/.vscode-server/bin/0ee08df0cf4527e40edc9aa28f4b5bd38bbff2b2/bin/remote-cli:/usr/local/cuda/bin:/usr/local/cuda/bin:/home/centos/.local/bin:/home/centos/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin)

sudo yum groupinstall "Development Tools"
sudo yum install gcc bzip2-devel libffi-devel

sudo yum install openssl11 openssl11-devel

<!-- 好像找不到 嘗試把3.12 python link到/usr/local/openssl
https://stackoverflow.com/questions/69371800/how-to-link-python3-to-use-openssl11-or-latest-version-of-openssl-1-1-1-on-c
./configure --enable-optimizations --with-openssl=/opt/openssl -->


[centos@fu-yuan Python-3.12.2]$ python3.12 --version
Python 3.12.2

[centos@fu-yuan Python-3.12.2]$ pip3.12 list
Package Version
------- -------
pip     24.0

然後 alias python3.12和 pip3.12給python和pip

alias python='python3.12'
alias pip='pip3.12'


pip install poetry==1.8.2


python3 -m venv .venv
source .venv/bin/activate

python -m venv .venv
source .venv/bin/activate


pip install packaging
pip install -r requirements.txt


安裝回3.10後 再試看看poetry
pip install poetry==1.8.2
