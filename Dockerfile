# Anaconda3 python distributionをベースContainerに利用
FROM continuumio/anaconda3
MAINTAINER kensuke-mi <kensuke.mit@gmail.com>

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
RUN apt-get install -y zlib1g-dev
### DB郡のインストール
RUN apt-get install -y python-psycopg2 postgresql postgresql-contrib libpq-dev
RUN apt-get install -y sqlite3
RUN apt-get install -y vim wget lsof curl
## boost1.57
RUN apt-get install -y build-essential g++ autotools-dev libicu-dev build-essential libbz2-dev
RUN wget http://downloads.sourceforge.net/project/boost/boost/1.57.0/boost_1_57_0.tar.bz2
RUN tar xvjf ./boost_1_57_0.tar.bz2 && cd boost_1_57_0 && ./bootstrap.sh --prefix=/opt/boost_1_57_0 && ./b2 && ./b2 install
# Install Boost
#WORKDIR /tmp
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
RUN wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://lotus.kuee.kyoto-u.ac.jp/nl-resource/jumanpp/jumanpp-1.02.tar.xz&name=jumanpp-1.02.tar.xz" -O jumanpp-1.02.tar.xz
RUN tar xJvf jumanpp-1.02.tar.xz
RUN cd jumanpp-1.02/ && ./configure && make && make install

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

### pyknpのインストールでコケること多いので、先にインストールしてしまう。
WORKDIR /opt
RUN wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://lotus.kuee.kyoto-u.ac.jp/nl-resource/pyknp/pyknp-0.3.tar.gz&name=pyknp-0.3.tar.gz" -O pyknp-0.3.tar.gz
RUN tar -xvf pyknp-0.3.tar.gz && cd pyknp-0.3 && python setup.py install
## Pythonパッケージのインストール
RUN conda install -y psycopg2 pymongo redis sqlalchemy numpy scipy pandas
RUN pip install jaconv
## Install packages for python with conda
RUN conda install -y numpy scipy scikit-learn cython psycopg2

### コード配置用のディレクトリ
RUN mkdir /codes
ADD . /codes/knp-utils
RUN cd /codes/knp-utils && python setup.py install

## Web appのバックエンドDBの作成 ##
USER postgres
### Postgresqlサービスのスタート && 管理用にdockerユーザーの作成。必ずコマンドの後にはserverをdownすること。
RUN /etc/init.d/postgresql start && psql -U postgres --command "CREATE USER docker WITH SUPERUSER PASSWORD 'docker';" && /etc/init.d/postgresql stop
### And add ``listen_addresses`` to ``/etc/postgresql/9.4/main/postgresql.conf``
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.4/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.4/main/postgresql.conf
### Expose the PostgreSQL port
### テーブルの初期化
WORKDIR /codes/knp-utils/web_api
RUN /etc/init.d/postgresql start && sleep 5 && psql postgres -f initialize_backend_db.sql && /etc/init.d/postgresql stop
## rootユーザーに戻す ##
USER root

EXPOSE 5432
EXPOSE 5000
WORKDIR /codes/knp-utils 
CMD ["/bin/bash", "start_web_server.sh"]