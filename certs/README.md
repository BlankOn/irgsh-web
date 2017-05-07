# BlankOn Root Certificate Authority

pembangkitan pasangan kunci untuk root CA menggunakan program `CA.pl` dengan argumen
`-newca`, dan tersimpan di bawah direktori `demoCA`. untuk sementara ini belum tahu 
bagaimana cara mengganti nama direktori tersebut. file pasangan kunci ada di file 
`cacert.pem` (bagian public) dan `private/cakey.pem` (bagian privat). 


## membuat sertifikat baru

    $ ./new-cert.sh <hostname-builder-yang-diinginkan>

keluaran skrip ini ada di direktori dengan nama hostname builder yang menjadi
argumen skrip ini. di dalam direktori ini ada beberapa file:

1. `newkey.pem`: private key untuk hostname ybs
1. `newcert.pem`: public key untuk hostname ybs
1. `newreq.pem`: CSR (certificate signing request) untuk hostname ybs.
file ini tidak diperlukan

## memasang sertifikat ke `irgsh-node` dan `irgsh-web`

TBD
membuat sertifikat baru
$ ./new-cert.sh <common-name-yang-diinginkan>


