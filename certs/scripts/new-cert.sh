#!/usr/bin/env bash
if [ "$1" == "" ]; then
    echo "usage: $0 <common-name>"
    exit 1
fi

#export 
env OPENSSL_CONF=konfigurasi/irgsh-openssl.cnf  SSLEAY_CONFIG="-subj \"/C=ID/ST=DKI Jakarta/L=Jakarta/O=BlankOn Linux/OU=Infrastruktur/CN=$1\"" ./scripts/ca.pl -newreq-nodes 
./scripts/ca.pl -sign
mkdir $1
mv new*.pem $1/
