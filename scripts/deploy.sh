#!/usr/bin/env bash

TOKEN=784d2329d009d54e3aa23b1926ab4b89f31e23be
RELEASE=v0.1

cd /tmp
wget --header "Authorization: token $TOKEN"  --output-document=$RELEASE.tar.gz https://github.com/kujonmobi/kujon-server/archive/RELEASE.tar.gz
