.ONESHELL:
run:
	cd jupyter_cobol_kernel
	docker build -t iladin/jupyter .
	docker run -v $(shell pwd):/tmp/jupyter_cobol_kernel/ -p 8888:8888 iladin/jupyter
