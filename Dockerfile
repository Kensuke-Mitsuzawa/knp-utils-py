FROM frolvlad/alpine-glibc:alpine-3.6
MAINTAINER kensuke-mi <kensuke.mit@gmail.com>

ENV JUMANPP_SOURCE_URL http://lotus.kuee.kyoto-u.ac.jp/nl-resource/jumanpp/jumanpp-1.02.tar.xz
ENV JUMAN_SOURCE_URL http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2
ENV KNP_SOURCE_URL http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.17.tar.bz2

ENV PATH=/opt/conda/bin:$PATH \
    LANG=C.UTF-8 \
    MINICONDA=Miniconda3-latest-Linux-x86_64.sh
# apk update
RUN apk update

# Python
RUN apk add --no-cache bash wget && \
    wget -q --no-check-certificate https://repo.continuum.io/miniconda/$MINICONDA && \
    bash /Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    ln -s /opt/conda/bin/* /usr/local/bin/ && \
    rm -rf /root/.[acpw]* /$MINICONDA /opt/conda/pkgs/*
# general
RUN apk --no-cache add vim wget lsof curl bash swig gcc build-base make python-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
# DB系システム
RUN apk --no-cache add sqlite
RUN apk --update add postgresql openssl && \
rm -f /var/cache/apk/* &&  \
wget --no-check-certificate  -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/1.4/gosu-amd64" &&  \
chmod +x /usr/local/bin/gosu &&  \
echo "Success"

# boost
RUN apk --no-cache add boost-dev

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
RUN cd knp-4.17 && ./configure && make && make install
RUN cd ../ && rm -rf knp-4.17
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
RUN mkdir /var/lib/postgresql/data
RUN mkdir /run/postgresql
ENV PGDATA /var/lib/postgresql/data
ENV PGRUN /run/postgresql
ENV POSTGRES_DB postgres
ENV POSTGRES_DOCKER_USER docker
ENV POSTGRES_DOCKER_PASSWORD docker

RUN chown -R postgres "$PGDATA"
RUN gosu postgres initdb
RUN sed -ri "s/^#(listen_addresses\s*=\s*)\S+/\1'*'/" "$PGDATA"/postgresql.conf
RUN pass="PASSWORD '$POSTGRES_DOCKER_PASSWORD'" && authMethod=md5


RUN createSql="CREATE DATABASE $POSTGRES_DB;"
RUN echo $createSql | gosu postgres postgres --single -jE  && echo
RUN userSql="CREATE USER $POSTGRES_DOCKER_USER WITH SUPERUSER $POSTGRES_DOCKER_PASSWORD;" && \
echo $userSql | gosu postgres postgres --single -jE && \
echo
RUN gosu postgres pg_ctl -D "$PGDATA" -o "-c listen_addresses=''" -w start
### テーブルの初期化
WORKDIR /codes/knp-utils/web_api
RUN psql postgres -f initialize_backend_db.sql

RUN gosu postgres pg_ctl -D "$PGDATA" -m fast -w stop
RUN { echo; echo "host all all 0.0.0.0/0 $authMethod"; } >> "$PGDATA"/pg_hba.conf

EXPOSE 5432
EXPOSE 5000
WORKDIR /codes/knp-utils
CMD ["/bin/bash", "start_web_server.sh"]