# Anaconda3 python distributionをベースContainerに利用
FROM continuumio/anaconda3
MAINTAINER kensuke-mi <kensuke.mit@gmail.com>

ENV REDIS_VERSION 3.2.8
ENV REDIS_HOME /opt/redis
RUN mkdir -p /opt
RUN mkdir -p ${REDIS_HOME}

## apt-getで依存ライブラリのインストール
RUN apt-get update
RUN apt-get install -y software-properties-common wget --fix-missing
#RUN add-apt-repository ppa:ubuntu-toolchain-r/test
RUN apt-get update

### gccのインストール
RUN apt-get install -y make --fix-missing
#RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 1
RUN apt-get install -y gcc --fix-missing
RUN apt-get install -y g++ --fix-missing
RUN apt-get install -y gcc-4.9 g++-4.9
RUN apt-get install -y swig2.0 --fix-missing
### DB郡のインストール
RUN apt-get install -y sqlite3
RUN apt-get install -y vim wget lsof curl
## boost1.57
# Install Boost
WORKDIR /tmp
#RUN curl -SL "http://downloads.sourceforge.net/project/boost/boost/1.62.0/boost_1_62_0.tar.bz2?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fboost%2Ffiles%2Fboost%2F1.62.0%2F&ts=$(date +%s)&use_mirror=superb-sea2" \
#    -o boost_1_62_0.tar.bz2 \
#  && [ $(sha1sum boost_1_62_0.tar.bz2 | awk '{print $1}') == '5fd97433c3f859d8cbab1eaed4156d3068ae3648' ] \
#  && tar --bzip2 -xf boost_1_62_0.tar.bz2 \
#  && cd boost_1_62_0 \
#  && ./bootstrap.sh --prefix=/usr/local \
#  && ./b2 -a -sHAVE_ICU=1 \
#  && ./b2 install \
#  && cd .. \
#  && rm -rf boost_1_62_0.tar.bz2 boost_1_62_0

## libunwind
#RUN apt-get install -y libunwind7-dev
### gperftools
#RUN mkdir -p /deps/gperftools
#RUN cd /deps; git clone "https://code.google.com/p/gperftools/"
#RUN cd /deps/gperftools;  git checkout gperftools-2.1; ./autogen.sh; ./configure --prefix=/usr; make; make install

## Juman
RUN apt-get install -y libcdb-dev libjuman
RUN wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2&name=juman-7.01.tar.bz2" -O juman-7.01.tar.bz2
RUN tar jxf juman-7.01.tar.bz2
WORKDIR /tmp/juman-7.01/
RUN ./configure && make  && make install
RUN apt-get -y install juman
RUN echo "これはテストの文です。" | juman

## Juman++
#RUN wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://lotus.kuee.kyoto-u.ac.jp/nl-resource/jumanpp/jumanpp-1.02.tar.xz&name=jumanpp-1.02.tar.xz" -O jumanpp-1.02.tar.xz
#RUN tar xJvf jumanpp-1.02.tar.xz
#RUN cd jumanpp-1.02/ && ./configure && make && make install

## KNP
WORKDIR /tmp
### -------------------------------------------------------------------------------------------
### 一般公開向けKNP-4.16を利用する場合は下のコード
RUN wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.16.tar.bz2&name=knp-4.16.tar.bz2" -O knp-4.16.tar.bz2
RUN tar jxf knp-4.16.tar.bz2
WORKDIR /tmp/knp-4.16
RUN ./configure && make && make install
### -------------------------------------------------------------------------------------------
RUN echo "私はさくらまなの作品が好きです。" | juman | knp

## Pythonパッケージのインストール
RUN conda install -y psycopg2 pymongo redis sqlalchemy numpy scipy pandas
RUN pip install jaconv

## Install redis server
RUN wget -q http://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz && \
    tar -zxvf redis-${REDIS_VERSION}.tar.gz && \
    mv redis-${REDIS_VERSION} redis-src && \
    cd redis-src && \
    make

## Install packages for python with conda
RUN conda install -y numpy scipy scikit-learn cython psycopg2
RUN pip install --user https://github.com/rogerbinns/apsw/releases/download/3.17.0-r1/apsw-3.17.0-r1.zip \
--global-option=fetch --global-option=--version --global-option=3.17.0 --global-option=--all \
--global-option=build --global-option=--enable-all-extensions
RUN pip install celery

### コード配置用のディレクトリ
RUN mkdir /codes
ADD . /codes/knp-utils
RUN cd /codes/knp-utils && python setup.py install

RUN mkdir /var/log/redis/
RUN mkdir /var/run/redis

EXPOSE 6379
EXPOSE 5000
WORKDIR /codes/DocumentFeatureSelection
CMD ["/bin/bash", "start_web_service.sh"]