FROM debian:stable-slim
MAINTAINER Herpiko Dwi Aguno <herpiko@gmail.com>
ENV DOCKYARD_SRC="."
ENV DOCKYARD_SRVHOME=/opt
ENV DOCKYARD_SRVPROJ=/opt/irgsh-web
COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ
EXPOSE 8000
RUN apt-get -y update && apt-get -y install make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils sudo \
python python-pip python-dev python-debian dpkg-dev rabbitmq-server git-core nginx libpq-dev git vim
WORKDIR $DOCKYARD_SRVPROJ
RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
RUN ~/.pyenv/bin/pyenv install 2.6.6
RUN export PATH=$PATH:/root/.pyenv/versions/2.6.6/bin
RUN /bin/bash -c "pip install -r requirements.txt"
