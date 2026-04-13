.PHONY: build build_sdist clean publish build_docker
SHELL = /bin/bash

# ----------------------------------------------------------------------------------------------------

pdm:
	@echo "Installing curl..."
	sudo apt-get install curl

	@echo "Installing pdm..."
	curl -sSL https://pdm-project.org/install-pdm.py | python3 -

	# If you meet problems with the above installation command, you can try the following command:
	# pip install --user pdm

# ----------------------------------------------------------------------------------------------------

build:
	@echo "Building..."
	# python -m pip install -U build && python -m build --wheel  
	pdm build --no-sdist -v

build_sdist:
	@echo "Building sdist..."
	pdm build -v

clean:
	@echo "Cleaning..."
	rm -rf build dist fourier_core.egg-info

publish:
	@echo "Publishing..."
	# twine upload --repository testpypi dist/*.whl
	pdm publish --no-build -v -u __token__ 

build_docker:
	@echo "Building in Docker image..."
	sudo rm -rf dist
	docker run --rm -it \
	--mount type=bind,source=$${PWD}/pyproject.toml,target=/project/pyproject.toml,readonly \
	--mount type=bind,source=$${PWD}/pdm.lock,target=/project/pdm.lock,readonly \
	--mount type=bind,source=$${PWD}/src/fourier_core,target=/project/src/fourier_core,readonly \
	--mount type=bind,source=$${PWD}/docs/README.md,target=/project/docs/README.md,readonly \
	-v $${PWD}/dist:/project/dist \
	yuxianggao/grx-build:latest
	sudo chown -R $${USER}:$${USER} dist/
