#OS:= $(shell uname)
ifeq (Linux,$(OS))
doIhave := which
installer := apt-get
printenv: ; $@ 
else
doIhave := where.exe
installer := scoop
printenv: ; SET
endif
ifeq (, $(shell $(doIhave) jupyter-notebook))
$(error "No jupyter-notebook in $(PATH), consider doing $(installer) install jupyter-notebook")
endif 
.ONESHELL:
run: ;  jupyter-notebook
docker:
#	cd jupyter_cobol_kernel
	docker build -t iladin/jupyter-cobol-kernel .
	docker run -v $(shell pwd):/tmp/jupyter_cobol_kernel/ -p 8888:8888 iladin/jupyter-cobol-kernel
lint: ; docker run -e RUN_LOCAL=true -v $(shell pwd):/tmp/lint github/super-linter
install: 
	pip3 $@ --no-cache-dir -e .
	cd jupyter_cobol_kernel && python3 install_cobol_kernel --user
