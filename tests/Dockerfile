FROM frolvlad/alpine-glibc:alpine-3.6
MAINTAINER kensuke-mi <kensuke.mit@gmail.com>

# Juman/Juman++
ENV JUMANPP_URL https://github.com/ku-nlp/jumanpp/releases/download/v2.0.0-rc2/jumanpp-2.0.0-rc2.tar.xz
ENV JUMAN_SOURCE_URL http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2
ENV KNP_SOURCE_URL http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.19.tar.bz2

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
RUN apk --no-cache add vim \
wget \
lsof \
curl \
bash \
swig \
gcc \
build-base \
make \
cmake \
jpeg-dev \
zlib-dev \
boost-dev \
linux-headers \
libexecinfo-dev
ENV LIBRARY_PATH=/lib:/usr/lib

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
# Juman++が求めるファイルパスが若干ちがうので、シンボリックリンクを作成
RUN ln /usr/include/linux/sysctl.h /usr/include/sys/sysctl.h
RUN wget $JUMANPP_URL \
    && tar xf jumanpp-2.0.0-rc2.tar.xz \
    && cd jumanpp-2.0.0-rc2/ \
    && mkdir bld \
    && cd bld/ \
    && cmake .. -DCMAKE_BUILD_TYPE=Release \
    && make install -j8 \
    && cd ../../ \
    && rm jumanpp-2.0.0-rc2.tar.xz \
    && rm -r jumanpp-2.0.0-rc2/
RUN echo "私はさくらまなの作品が好きです。" | jumanpp

## KNP
WORKDIR /tmp
### -------------------------------------------------------------------------------------------
### 一般公開向けKNP-4.16を利用する場合は下のコード
RUN wget ${KNP_SOURCE_URL}
RUN tar xfj knp-4.19.tar.bz2
RUN cd knp-4.19 && ./configure && make && make install
RUN cd ../ && rm -rf knp-4.19
RUN echo "私はさくらまなの作品が好きです。" | jumanpp | knp


### -------------------------------------------------------------------------------------------
### Install python packages
WORKDIR /opt
## Pythonパッケージのインストール

RUN conda config --add channels conda-forge --system
RUN conda create -y -n p27 python=2.7
RUN conda create -y -n p36 python=3.6
RUN conda create -y -n p37 python=3.7