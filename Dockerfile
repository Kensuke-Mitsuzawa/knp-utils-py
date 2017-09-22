FROM frolvlad/alpine-glibc:alpine-3.6
MAINTAINER kensuke-mi <kensuke.mit@gmail.com>

ENV JUMANPP_SOURCE_URL http://lotus.kuee.kyoto-u.ac.jp/nl-resource/jumanpp/jumanpp-1.02.tar.xz
ENV JUMAN_SOURCE_URL http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2
ENV KNP_SOURCE_URL http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.17.tar.bz2

ENV PATH=/opt/conda/bin:$PATH \
    LANG=C.UTF-8 \
    MINICONDA=Miniconda3-latest-Linux-x86_64.sh

# Python
RUN apk add --no-cache bash wget && \
    wget -q --no-check-certificate https://repo.continuum.io/miniconda/$MINICONDA && \
    bash /Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    ln -s /opt/conda/bin/* /usr/local/bin/ && \
    rm -rf /root/.[acpw]* /$MINICONDA /opt/conda/pkgs/*
# general
RUN apk --no-cache add vim wget lsof curl bash swig gcc build-base make
# DB系システム
RUN apk --no-cache add sqlite postgresql
# boost
RUN apk --no-cache add boost-dev

#RUN \
#  apk add --no-cache --virtual .build-deps g++ make curl linux-headers python-dev \
#  && curl -SL "http://downloads.sourceforge.net/project/boost/boost/1.62.0/boost_1_62_0.tar.bz2?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fboost%2Ffiles%2Fboost%2F1.62.0%2F&ts=$(date +%s)&use_mirror=superb-sea2" \
#    -o boost_1_62_0.tar.bz2 \
#  && [ $(sha1sum boost_1_62_0.tar.bz2 | awk '{print $1}') == '5fd97433c3f859d8cbab1eaed4156d3068ae3648' ] \
#  && tar --bzip2 -xf boost_1_62_0.tar.bz2 \
#  && cd boost_1_62_0 \
#  && ./bootstrap.sh --prefix=/usr/local \
#  && ./b2 -a -sHAVE_ICU=1 \
#  && ./b2 install \
#  && cd .. \
#  && rm -rf boost_1_62_0.tar.bz2 boost_1_62_0

# directory
WORKDIR /tmp

## Juman
RUN wget ${JUMAN_SOURCE_URL} -O juman-source.tar.bz2
RUN tar xfj juman-source.tar.bz2
RUN cd juman-7.01 && ./configure && make && make install
WORKDIR /tmp
RUN rm juman-source.tar.bz2
RUN rm -rf juman-7.01
RUN echo "私はさくらまなの作品が好きです。" | juman

## Juman++
RUN wget ${JUMANPP_SOURCE_URL}
RUN tar Jxfv jumanpp-1.02.tar.xz
RUN cd jumanpp-1.02 && ./configure && make && make install
WORKDIR /tmp
RUN rm -rf jumanpp-1.02 jumanpp-1.02.tar.xz
RUN echo "私はさくらまなの作品が好きです。" | jumanpp

## KNP
WORKDIR /tmp
### -------------------------------------------------------------------------------------------
### 一般公開向けKNP-4.16を利用する場合は下のコード
RUN wget ${KNP_SOURCE_URL}
RUN tar xfj knp-4.17.tar.bz2
RUN cd cd /knp-4.17 && ./configure && make && make install
RUN cd ../ && rm knp-4.17.tar.bz2 && rm -rf knp-4.17
RUN echo "私はさくらまなの作品が好きです。" | jumanpp | knp


### -------------------------------------------------------------------------------------------
### Install python packages
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