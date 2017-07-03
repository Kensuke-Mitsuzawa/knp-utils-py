#!/usr/bin/env bash

os_type=`uname`
WORK_DIR=`pwd`

echo "os-type is "$os_type
if [ `uname` = "Darwin" ]; then
    #mac用のコード
    juman_utils_bin="/usr/local/opt/juman/libexec/juman/"
    if [ -e ${juman_utils_bin} ]; then
        :
    else
        juman_utils_bin="/usr/local/libexec/juman/"
    fi
elif [ `uname` = "Linux" ]; then
    #Linux用のコード
    juman_utils_bin="/usr/local/libexec/juman/"
else
    echo "Your platform ($(uname -a)) is not supported."
    exit 1
fi


cd $WORK_DIR
echo 'これはテスト' | juman
is_juman_install=$?

if [ $is_juman_install -eq 127 ]; then
    ## juman
    wget -O juman7.0.1.tar.bz2 "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2&name=juman-7.01.tar.bz2"
    bzip2 -dc juman7.0.1.tar.bz2  | tar xvf -
    cd juman-7.01 && ./configure && make && make install
    # インストール後のldconfig
    ldconfig
    # 動作テスト
    echo 'インストール後のテスト' | juman
else
    :
fi

cd $WORK_DIR
echo 'これはテスト' | jumanpp
is_jumanpp_install=$?

if [ $is_jumanpp_install -eq 127 ]; then
    # jumanpp
    wget http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://lotus.kuee.kyoto-u.ac.jp/nl-resource/jumanpp/jumanpp-1.02.tar.xz&name=jumanpp-1.02.tar.xz -O jumanpp-1.02.tar.xz
    tar xJvf jumanpp-1.02.tar.xz
    cd jumanpp-1.02/
    ./configure && make && make install
    # インストール後のldconfig
    ldconfig
    # 動作テスト
    echo 'インストール後のテスト' | jumanpp
else
    :
fi

cd $WORK_DIR
echo 'これはテスト' | juman | knp
is_knp_install=$?

if [ $is_knp_install -eq 127 ]; then
    # install knp
    wget -O knp-4.17.tar.bz2 "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.17.tar.bz2&name=knp-4.17.tar.bz2"
    tar jxf knp-4.17.tar.bz2
    cd /knp-4.17
    ./configure && make  && make install
else
    :
fi

cd $WORK_DIR

if [ -f ./juman7.0.1.tar.bz2 ]; then
    # juman
	rm juman7.0.1.tar.bz2
else
    :
fi

if [ -d ./juman-7* ]; then
	# kytea
	rm -rf juman-7*
else
    :
fi


if [ -f ./jumanpp-1.02.tar.xz ]; then
	# jumanpp
	rm jumanpp-1.02.tar.xz
else
    :
fi

if [ -d ./jumanpp-1.01 ]; then
	rm -rf jumanpp-1.01
else
    :
fi

if [ -d ./knp-4.17 ]; then
    rm -rf knp-4.17
else
    :
fi

if [ -f knp-4.17.tar.bz2 ]; then
    rm knp-4.17.tar.bz2
else
    :
fi