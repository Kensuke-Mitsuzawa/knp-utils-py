#!/usr/bin/env bash
BASE_DIR=`pwd`
gosu postgres pg_ctl -o "-c listen_addresses='*'" -w start

cd ./web_api
python app.py
