FROM jupyter/minimal-notebook

USER root

# Install vim and ssh
RUN apt-get update
RUN apt-get install -y vim openssh-client

WORKDIR /tmp

COPY ./ jupyter_cobol_kernel/

RUN pip3 install --no-cache-dir -e jupyter_cobol_kernel/ | tee piplog.txt
RUN  cd jupyter_cobol_kernel/jupyter_cobol_kernel && python3 install_cobol_kernel --user | tee installlog.txt

WORKDIR /home/$NB_USER/

USER $NB_USER
