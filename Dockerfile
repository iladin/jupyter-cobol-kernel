#FROM jupyter/minimal-notebook
FROM ubuntu:18.04
USER root

ARG gnucobol_version=3.1.2
ARG version=gnucobol-${gnucobol_version}

#hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -y vim openssh-client build-essential ca-certificates wget gcc make libdb-dev libncurses5-dev libgmp-dev autoconf gpg && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

RUN wget https://gnu.mirror.constant.com/gnucobol/${version}.tar.gz \
         https://gnu.mirror.constant.com/gnucobol/${version}.tar.gz.sig
#         https://ftp.gnu.org/gnu/gnu-keyring.gpg && gpg --verify --keyring ./gnu-keyring.gpg ${version}.tar.gz.sig

RUN tar zxf ${version}.tar.gz

WORKDIR ${version}
RUN ./configure
RUN make
RUN make install
RUN make check
RUN ldconfig
RUN cobc --version

COPY ./ jupyter_cobol_kernel/

RUN pip3 install --no-cache-dir -e jupyter_cobol_kernel/
WORKDIR /tmp/jupyter_cobol_kernel
RUN python3 install_cobol_kernel --user

WORKDIR /home/$NB_USER/

USER $NB_USER
