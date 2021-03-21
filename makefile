.ONESHELL:
run:
#	cd jupyter_cobol_kernel
	docker build -t iladin/jupyter-cobol-kernel .
	docker run -v $(shell pwd):/tmp/jupyter_cobol_kernel/ -p 8888:8888 iladin/jupyter-cobol-kernel
lint: ; docker run -e RUN_LOCAL=true -v $(shell pwd):/tmp/lint github/super-linter
