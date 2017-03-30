# irgsh-web
irgsh web interface

### [Draft] Petunjuk Instalasi
==================

DRAFT DRAFT DRAFT DRAFT DRAFT DRAFT DRAFT DRAFT DRAFT DRAFT DRAFT DRAFT DRAFT


Persiapan Administrasi
----------------------

1. Sertifikat CA Irgsh (irgsh-ca.pem)
1. Sertifikat SSL untuk web server (irgsh.pem, irgsh.key)
2. Sertifikat SSL untuk pekerja penyiap tugas (taskinit.pem, taskinit.key)
3. Sertifikat SSL untuk RabbitMQ (rabbitmq.pem, rabbitmq.key)
3. Kunci SSH (taskinit-ssh.key)


Kebutuhan
---------

1. Python 2.6
2. RabbitMQ
3. dpkg-dev
4. nginx
5. git (untuk mengunduh kode sumber)

Pengguna sistem operasi berbasis Debian dapat menjalankan perintah berikut
untuk memasang semua kebutuhan.

		$ apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils sudoers python python-pip python-dev python-debian dpkg-dev rabbitmq-server git-core nginx libpq-dev git vim

Instalasi
---------

### Unduh kode sumber

    $ git clone git://github.com/BlankOn/python-irgsh.git
    $ git clone git://github.com/BlankOn/web-interfaces.git
    $ git clone git://github.com/BlankOn/irgsh-node.git
    $ git clone git://github.com/BlankOn/irgsh-repo.git
    $ cd web-interfaces
    $ ln -s ../python-irgsh/irgsh
    $ ln -s ../irgsh-node/irgsh_node
    $ ln -s ../irgsh-repo/irgsh_repo

### Persiapkan kode sumber

    $ python bootstrap.py
    $ ./bin/buildout


Konfigurasi
-----------

### Konfigurasi RabbitMQ

Konfigurasi hak akses

    $ sudo rabbitmqctl add_user irgsh irgsh
    $ sudo rabbitmqctl add_vhost irgsh
    $ sudo rabbitmqctl set_permissions -p irgsh irgsh '.*' '.*' '.*'

Konfigurasi koneksi dengan SSL

    $ sudo cp rabbitmq.pem rabbitmq.key /etc/rabbitmq
    $ cat ca.pem irgsh-ca.pem | sudo tee /etc/rabbitmq/ca-certs.pem
    $ sudo vi /etc/rabbitmq/rabbitmq.config
    $ sudo cat /etc/rabbitmq/rabbitmq.config
    [
      {rabbit, [
         {ssl_listeners, [{"0.0.0.0",5671}]},
         {ssl_options, [{cacertfile,"/etc/rabbitmq/ca-certs.pem"},
                        {certfile,"/etc/rabbitmq/rabbitmq.pem"},
                        {keyfile,"/etc/rabbitmq/rabbitmq.key"},
                        {verify,verify_peer},
                        {depth,2},
                        {fail_if_no_peer_cert,true}]}
       ]}
    ].

Restart RabbitMQ.

    $ sudo /etc/init.d/rabbitmq-server restart

Tutup koneksi tanpa SSL dari luar menuju RabbitMQ.

    $ sudo iptables -A INPUT -p tcp --dport 5672 -j REJECT

Simpan konfigurasi iptables dengan `iptables-save` dan pastikan konfigurasi
dipasang kembali setiap mesin dihidupkan.


Verifikasi koneksi SSL dengan perintah berikut. Jika berhasil, maka
informasi sertifikat akan ditampilkan.

    $ openssl s_client -cert taskinit.pem -key taskinit.key \
                       -connect localhost:5671


### Konfigurasi Irgsh

Sunting berkas `irgsh_web/localsettings.py` dan tambahkan variabel-variabel
berikut.

    # Sertifikat pekerja penyiap tugas
    SSL_KEY = 'local/taskinit.key'
    SSL_CERT = 'local/taskinit.pem'

    # Konfigurasi antrian
    BROKER_HOST = '127.0.0.1'
    BROKER_PORT = 5671
    BROKER_USER = 'irgsh'
    BROKER_PASSWORD = 'irgsh'
    BROKER_VHOST = 'irgsh'

    # Lokasi upload paket kode sumber
    SOURCE_UPLOAD_HOST = '192.168.56.202'
    SOURCE_UPLOAD_USER = 'upload'
    SOURCE_UPLOAD_PORT = 22
    SOURCE_UPLOAD_KEY = 'local/taskinit-ssh.key'

    # Lokasi Irgsh
    SERVER = 'https://192.168.1.1:8443/'

    # Lokasi penyimpanan log
    LOG_PATH = 'run/logs'

    # Lokasi paket kode sumber bagi pekerja
    DOWNLOAD_TARGET = 'static/source/'

    # Basis data
    DATABASES = {
        'default': {
            'ENGINE': 'sqlite3',
            'NAME': 'irgsh.db',
        }
    }


Persiapkan basis data.

    $ ./bin/django syncdb


### Konfigurasi nginx

Salin berkas `nginx.conf` ke `/etc/nginx/sites-available/irgsh.conf` dan
sesuaikan hal-hal berikut.

1. Lokasi kode sumber, default: `/srv/irgsh_web`
2. Lokasi berkas paket kode sumber, default: `/srv/irgsh_web/static/source`.
   Sesuaikan dengan nilai konfigurasi `DOWNLOAD_TARGET`
3. Lokasi berkas log dan changes, default: `/srv/irgsh_web/run/logs/...`.
   Sesuaikan dengan nilai konfigurasi `LOG_PATH`
4. Nama server pada `server_name`.
5. Lokasi sertifikat pada `ssl_client_certificate, `ssl_certificate`, dan
   `ssl_certificate_key`.
6. Koneksi FastCGI dengan Django. Sesuaikan dengan cara menjalankan Django.
   Konfigurasi default mengharapkan Django menjalankan FastCGI melalui
   TCP socket pada `localhost` port `18000`.


Eksekusi
--------

Ada dua hal yang harus dijalankan:

1. Django server

        $ ./bin/django runfcgi method=prefork host=127.0.0.1 port=18000

2. TaskInit worker

        $ ./bin/django celeryd -n taskinit
