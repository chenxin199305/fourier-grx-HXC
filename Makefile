SHELL := /bin/bash

.PHONY: all fast nuitka pyinstaller blaze pack rename test echo_version \
        pack_zip pack_deb \
        rename_zip rename_deb rename_deb_nuitka rename_deb_pyinstaller rename_deb_test rename_deb_blaze \
        zip_bin zip_bin_whl \
        deb_prepare deb_finish deb_bin deb_bin_whl \
        bin_from_nuitka bin_from_pyinstaller bin_zip whl_file \
        update_env build build_sdist clean clean_all publish

# Build environment prerequisites:
#   1. conda install libpython-static   (Nuitka inside a conda env)
#   2. sudo apt install patchelf        (Nuitka linker helper)
#   3. sudo apt install ccache          (Nuitka compile cache)
#   4. sudo apt install dpkg            (deb packaging)
#   5. sudo apt install fakeroot        (deb packaging)
#   6. CPU-only PyTorch:
#        pip uninstall torch
#        pip install torch --index-url https://download.pytorch.org/whl/cpu

# Notes:
#   "fourier-grx"  — software / deb package name
#   "fourier_grx"  — Python package name (underscores)
#
#   Before running make, execute `pip install -e .` to ensure the installed
#   version matches the source; otherwise the packaged binary may report the
#   wrong version.
#
#   make / make all  — source-free Nuitka build (~30 min); produces .deb + wheels
#   make fast        — source-preserved PyInstaller build (~15 min); do NOT publish
#   make test        — binary-only, no secondary whl wheels (~5 min); do NOT publish

# =============================================================================
# Platform info
# =============================================================================
OS      := $(shell uname -s | tr A-Z a-z)
ARCH    := $(shell dpkg --print-architecture 2>/dev/null || uname -m)
BACKEND := cpu
PLATFORM := $(OS)-$(ARCH)-$(BACKEND)

# =============================================================================
# Git info
# =============================================================================
GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)

# =============================================================================
# Version
# =============================================================================
GET_VERSION := $(shell pip show fourier-grx 2>/dev/null | grep Version | awk '{print $$2}')
ifeq ($(strip $(GET_VERSION)),)
GET_VERSION := 0.0.1
endif

# =============================================================================
# Robot type (defaults to hxc on this branch)
# =============================================================================
ROBOT ?= hxc

ifeq ($(strip $(ROBOT)),)
PLATFORM_ROBOT := $(PLATFORM)
else
PLATFORM_ROBOT := $(PLATFORM)-$(ROBOT)
endif

# =============================================================================
# Deb naming
# =============================================================================
DEB_BASENAME := fourier-grx-$(GET_VERSION)-$(PLATFORM_ROBOT)

# =============================================================================
# Path setup
# =============================================================================
DES_CONFIG_DIR   := dist/zip/config/
DES_RESOURCE_DIR := dist/zip/resource/

ifeq ($(strip $(ROBOT)),)
SRC_CONFIG_DIR   := config
SRC_RESOURCE_DIR := resource
else
SRC_CONFIG_DIR   := config/$(ROBOT)
SRC_RESOURCE_DIR := resource/$(ROBOT)
endif

# =============================================================================
# Top-level targets
# =============================================================================
# pdm build cleans the dist folder, so whl files must be built first.
all: nuitka
	@echo "Build finished."

fast: pyinstaller
	@echo "Fast build finished."

nuitka: clean_all update_env whl_file bin_from_nuitka zip_bin_whl deb_bin_whl rename_zip rename_deb_nuitka
	@echo "Nuitka build finished."

pyinstaller: clean_all update_env whl_file bin_from_pyinstaller zip_bin_whl deb_bin_whl rename_zip rename_deb_pyinstaller
	@echo "PyInstaller build finished."

blaze: clean_all update_env bin_from_pyinstaller zip_bin deb_bin rename_zip rename_deb_blaze
	@echo "Blaze (ultra-fast) build finished."

pack: pack_zip pack_deb
	@echo "Packing finished."

rename: rename_zip rename_deb
	@echo "Renaming finished."

test: clean_all update_env bin_from_pyinstaller deb_bin rename_deb_test
	@echo "Test build finished."

echo_version:
	@echo "Current version: $(GET_VERSION)"

# =============================================================================
# Rename helpers
# =============================================================================
pack_zip: zip_bin_whl rename_zip
pack_deb: deb_bin_whl rename_deb

rename_zip:
	@echo "Renaming zip..."
	rm -f dist/fourier-grx-*.zip
	mv dist/fourier-grx.zip dist/fourier-grx-$(GET_VERSION).zip

rename_deb:
	@echo "Renaming deb..."
	rm -f dist/fourier-grx-*.deb
	mv dist/fourier-grx.deb dist/$(DEB_BASENAME).deb

rename_deb_nuitka: rename_deb
	mv dist/$(DEB_BASENAME).deb dist/$(DEB_BASENAME)-nuitka.deb

rename_deb_pyinstaller: rename_deb
	mv dist/$(DEB_BASENAME).deb dist/$(DEB_BASENAME)-pyinstaller.deb

rename_deb_test: rename_deb
	mv dist/$(DEB_BASENAME).deb dist/$(DEB_BASENAME)-test.deb

rename_deb_blaze: rename_deb
	mv dist/$(DEB_BASENAME).deb dist/$(DEB_BASENAME)-blaze.deb

# =============================================================================
# ZIP packaging
# =============================================================================
zip_bin:
	@echo "Building zip..."
	rm -f dist/fourier-grx.zip
	mkdir -p dist/zip
	rm -rf dist/zip/*
	cp dist/run.bin dist/zip/run.bin
	mkdir -p $(DES_CONFIG_DIR) $(DES_RESOURCE_DIR)
	cp -r $(SRC_CONFIG_DIR) $(DES_CONFIG_DIR)
	cp -r $(SRC_RESOURCE_DIR) $(DES_RESOURCE_DIR)
	cp release/setup.sh  dist/zip/setup.sh
	cp release/config.sh dist/zip/config.sh
	cp release/list.sh   dist/zip/list.sh
	cp release/run.sh    dist/zip/run.sh
	mkdir -p dist/zip/script
	cp release/setup_ubuntu_env.sh       dist/zip/script/
	cp release/setup_pass_sudo.sh        dist/zip/script/
	cp release/setup_disable_ipv6.sh     dist/zip/script/
	cp release/setup_static_ipv4.sh      dist/zip/script/
	cp release/setup_enable_service.sh   dist/zip/script/
	cp release/setup_disable_service.sh  dist/zip/script/
	cp release/setup_conda_env.sh        dist/zip/script/
	cp release/setup_conda_env_py310.sh  dist/zip/script/
	mkdir -p dist/zip/driver
	cp release/grce-net_2.0.0-2.deb dist/zip/driver/
	mkdir -p dist/zip/doc
	cp release/joystick_type_a.png dist/zip/doc/
	cp release/joystick_type_b.png dist/zip/doc/
	cp release/joystick_type_c.png dist/zip/doc/
	cp -r lib/ dist/zip/lib/
	cd dist/zip && zip -r ../fourier-grx.zip ./*

zip_bin_whl: zip_bin
	@echo "Adding whl files to zip..."
	rm -f dist/fourier-grx.zip
	mkdir -p dist/zip/whl
	rm -rf dist/zip/whl/*
	cp dist/fourier_grx-*.whl             dist/zip/whl/
	cp fourier-core/dist/fourier_core-*.whl dist/zip/whl/
	cp release/run.py                     dist/zip/whl/run.py
	cd dist/zip && zip -r ../fourier-grx.zip ./*

# =============================================================================
# DEB packaging
# =============================================================================
deb_prepare:
	@echo "Preparing deb package..."
	rm -f dist/fourier-grx.deb
	mkdir -p dist/deb
	rm -rf dist/deb/*
	mkdir -p dist/deb/fourier-grx/DEBIAN
	mkdir -p dist/deb/fourier-grx/usr/local/bin
	mkdir -p dist/deb/fourier-grx/usr/share/fourier-grx
	cp release/deb_control.in  dist/deb/fourier-grx/DEBIAN/control
	cp release/deb_postinst.sh dist/deb/fourier-grx/DEBIAN/postinst
	cp release/deb_postrm.sh   dist/deb/fourier-grx/DEBIAN/postrm
	chmod +x dist/deb/fourier-grx/DEBIAN/postinst
	chmod +x dist/deb/fourier-grx/DEBIAN/postrm
	cp release/deb_run.sh dist/deb/fourier-grx/usr/local/bin/fourier-grx
	chmod +x dist/deb/fourier-grx/usr/local/bin/fourier-grx
	cp dist/fourier-grx.zip dist/deb/fourier-grx/usr/share/fourier-grx/fourier-grx.zip

deb_finish: deb_prepare
	@echo "Generating deb control file..."
	sed -i \
		-e "s/__VERSION__/$(GET_VERSION)/g" \
		-e "s/__BRANCH__/$(GIT_BRANCH)/g" \
		-e "s/__ARCH__/$(ARCH)/g" \
		-e "s/__PLATFORM__/$(PLATFORM)/g" \
		dist/deb/fourier-grx/DEBIAN/control
	@echo "Building deb package..."
	dpkg-deb --build dist/deb/fourier-grx dist/fourier-grx.deb

deb_bin:     zip_bin     deb_finish
deb_bin_whl: zip_bin_whl deb_finish

# =============================================================================
# Binary build
# =============================================================================
bin_from_nuitka:
	@echo "Building binary with Nuitka..."
	pdm run build_bin_nuitka

bin_from_pyinstaller:
	@echo "Building binary with PyInstaller..."
	pdm run build_bin_pyinstaller
	mv dist/run dist/run.bin

bin_zip: bin_from_nuitka zip_bin
	@echo "Binary zip finished."

whl_file:
	@echo "Building fourier_grx wheel..."
	rm -rf dist/fourier_grx-*.whl
	pdm build --no-sdist -v --no-clean
	@echo "Building fourier_core wheel..."
	cd fourier-core && \
	rm -rf dist/fourier_core-*.whl && \
	pdm build --no-sdist -v --no-clean

# =============================================================================
# Environment
# =============================================================================
update_env:
	@echo "Installing fourier-grx (editable)..."
	pip install -e .
	@echo "Installing fourier-core (editable)..."
	cd fourier-core && pip install -e .

# =============================================================================
# Wheel / sdist / publish
# =============================================================================
build:
	@echo "Building wheel..."
	pdm build --no-sdist -v --no-clean

build_sdist:
	@echo "Building sdist..."
	pdm build -v --no-clean

clean:
	@echo "Cleaning..."
	rm -rf build dist fourier_grx.egg-info

clean_all:
	@echo "Cleaning all..."
	rm -rf build dist fourier_grx.egg-info
	rm -rf fourier-core/build fourier-core/dist fourier-core/fourier_core.egg-info

publish:
	@echo "Publishing..."
	pdm publish --no-build -v -u __token__
