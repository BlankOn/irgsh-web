#!/usr/bin/env bash
# Renew ssl pabrik yg sudah ada. Cara pakai : $renew-ssl.sh namapabrik
if [ "$1" == "" ]; then
    echo "usage: $0 <common-name>"
    exit 1
fi

export OPENSSL_CONF=conf/irgsh-openssl.cnf
if [ ! -d expired.`date +%Y` ]; then mkdir expired.`date +%Y`; fi
mv $1/ expired.`date +%Y`/
echo $1
env SSLEAY_CONFIG="-subj \"/C=ID/ST=DKI Jakarta/L=Jakarta/O=BlankOn Linux/OU=Infrastruktur/CN=$1\"" ./scripts/ca.pl -newreq-nodes 
./scripts/ca.pl -sign
mkdir $1
mv new*.pem $1/
