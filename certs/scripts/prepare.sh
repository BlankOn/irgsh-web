mkdir -p demoCA/private
mkdir -p demoCA/newcerts
mkdir -p demoCA/certs
touch demoCA/index.txt
touch demoCA/crlnumber
touch demoCA/serial
echo '01' > demoCA/serial
mv newcert.pem demoCA/cacert.pem
mv newkey.pem demoCA/private/cakey.pem
