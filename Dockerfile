FROM jupyter/minimal-notebook

USER root

# Install vim and ssh
RUN apt-get update
RUN apt-get install -y vim openssh-client wget gcc make libdb-dev libncurses5-dev libgmp-dev autoconf gpg

WORKDIR /tmp

RUN wget https://gnu.mirror.constant.com/gnucobol/gnucobol-3.1.tar.gz \
         https://gnu.mirror.constant.com/gnucobol/gnucobol-3.1.tar.gz.sig \
         https://ftp.gnu.org/gnu/gnu-keyring.gpg
#RUN gpg --verify --keyring ./gnu-keyring.gpg gnucobol-3.1.tar.gz.sig
RUN tar zxf gnucobol-3.1.tar.gz

WORKDIR gnucobol-3.1
RUN ./configure
RUN make
RUN make install
RUN make check
RUN ldconfig
RUN cobc --version

COPY ./ jupyter_cobol_kernel/

RUN pip3 install --no-cache-dir -e jupyter_cobol_kernel/ | tee piplog.txt
RUN cd jupyter_cobol_kernel/jupyter_cobol_kernel && python3 install_cobol_kernel --user | tee installlog.txt

WORKDIR /home/$NB_USER/

USER $NB_USER
