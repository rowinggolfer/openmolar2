define USEAGE 
This is the build script for openmolar packages and tarballs.

USAGE
   make [options] target

OPTIONS
   SUFFIX        (the second part of the package name client, admin etc...)    
       default=namespace
       allowed values namespace, client, common, admin, server
   DIST          (the target distribution - eg. unstable, squeeze, lucid etc.) 
       default=unstable
       allowed values - anything.. 
       but if building a deb, have a pbuilder environment with this name    
   DEBHELPER     (specifies with python system to use for debian source packages)                    
       allowed=py_support, dh_python2
       default=dh_python2
   NEW_CHANGELOG (run a gui to modify the changelog)
       default=true

TARGETS
   tarball 
   deb_src
   deb_binary
   all_tarballs
   all_deb_srcs
   all_deb_binaries
   
EXAMPLES are available.
	make examples
endef

define EXAMPLES
EXAMPLES
make tarball
	create a tarball for the default package (openmolar-namespace)   
make tarball SUFFIX=client
	create a tarball for openmolar-client   
make all_tarballs
	create tarballs for ALL suffixes

make deb_src DIST=squeeze SUFFIX=client
	create a debian source package for openmolar-client 
make deb_src DIST=lucid SUFFIX=admin DEBHELPER=py_support
	create a debian source package for ubuntu lucid (10.04)
	NOTE - lucid predates dh_python2, so debs MUST specify py_support instead.
make deb_binary DIST=precise SUFFIX=server 
	create a debian binary package for ubuntu precise (12.04).


and here's the whole shebang (as of April 24 2012) - should be a loop really

make all_tarballs
make all_deb_srcs DIST=lucid DEBHELPER=py_support
make all_deb_srcs DIST=squeeze 
make all_deb_srcs DIST=wheezy NEW_CHANGELOG=false
make all_deb_srcs DIST=unstable NEW_CHANGELOG=false
make all_deb_srcs DIST=oneiric NEW_CHANGELOG=false
make all_deb_srcs DIST=precise NEW_CHANGELOG=false
make all_deb_binaries DIST=lucid
make all_deb_binaries DIST=squeeze
make all_deb_binaries DIST=wheezy
make all_deb_binaries DIST=unstable
make all_deb_binaries DIST=oneiric
make all_deb_binaries DIST=precise

endef
	
export USEAGE
export EXAMPLES

ifeq ($(SUFFIX), )
	SUFFIX=namespace
endif

ifeq ($(DIST), )
	DIST=unstable
endif

ifeq ($(DEBHELPER), )
	DEBHELPER=dh_python2
endif

ifeq ($(NEW_CHANGELOG), )
	NEW_CHANGELOG=true
endif


PACKAGE=openmolar-$(SUFFIX)

HEAD=$(HOME)/openmolar/hg_openmolar/
BUILD_SCRIPTS_DIR = $(HEAD)/build_scripts/
BUILDS_DIR=$(HEAD)builds/$(SUFFIX)/

DIST_DIR=$(HEAD)dist/
DEB_CONF_DIR=$(HEAD)build_scripts/$(SUFFIX)/debian_packaging/$(DEBHELPER)/debian/

VERSION=`$(BUILD_SCRIPTS_DIR)/get_version.py $(SUFFIX)`

TARBALL = $(PACKAGE)-$(VERSION).tar.gz
TARBALL_DIR=$(HEAD)builds/$(SUFFIX)/tarballs/

TMP_DIR=$(HEAD)tmp/

DEB_SRCBUILDS_DIR=$(BUILDS_DIR)deb_srcs/$(DIST)/
DEB_BUILDS_DIR=$(BUILDS_DIR)debs/$(DIST)/


#this is where pbuilder puts stuff
CACHE=/var/cache/pbuilder/$(DIST)-amd64/result/

.phony:
	make help

help:
	@echo "$$USEAGE"

examples:
	@echo "$$EXAMPLES"
	
clean_tmp:
	mkdir -p $(TMP_DIR)
	rm -rf $(TMP_DIR)/*

tarball:
	echo "making $(SUFFIX) tarball"
	mkdir -p $(TARBALL_DIR)
	cd $(HEAD) ;\
		python configure.py --$(SUFFIX) ;\
		python setup.py sdist ;\
	cp -av $(DIST_DIR)$(TARBALL) $(TARBALL_DIR);
	@echo "tarball is located $(TARBALL_DIR)$(TARBALL)"

	@if [ -e "$(TARBALL_DIR)$(TARBALL)" ]; then echo "SUCCESS!"; fi
	
all_tarballs:
	make SUFFIX=namespace tarball
	make SUFFIX=common tarball
	make SUFFIX=client tarball
	make SUFFIX=admin tarball
	make SUFFIX=server tarball
	
all_deb_srcs:
	make SUFFIX=namespace deb_src
	make SUFFIX=common deb_src
	make SUFFIX=client deb_src
	make SUFFIX=admin deb_src
	make SUFFIX=server deb_src

all_deb_binaries:
	make SUFFIX=namespace deb_binary
	make SUFFIX=common deb_binary
	make SUFFIX=client deb_binary
	make SUFFIX=admin deb_binary
	make SUFFIX=server deb_binary
		
sign_tarball:
	cd $(TARBALL_DIR) ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(TARBALL) ;\
	md5sum $(TARBALL) | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	
	
deb_src:
	@if [ ! -e "$(TARBALL_DIR)$(TARBALL)" ]; then make tarball; fi
	
	make clean_tmp

	@echo "target distro = $(DIST)"
	
	# call my changelog gui	
	@if [ "$(NEW_CHANGELOG)" = 'true' ]; then \
		$(BUILD_SCRIPTS_DIR)deb_maker.py -s$(TARBALL_DIR) -d$(DEB_CONF_DIR) -popenmolar-$(SUFFIX); \
	fi
	cp -av $(TARBALL_DIR)$(TARBALL) $(TMP_DIR)
	
	cd $(TMP_DIR) ;\
	tar -zxvf $(TARBALL); \
	mv $(TARBALL) `$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR)`.orig.tar.gz 
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; \
	cp -av $(DEB_CONF_DIR) . ;\
	echo "modding changelog" ;\
	sed -i s/__DIST__/$(DIST)/g debian/changelog ;\
	dpkg-buildpackage -us -uc -S -kF230408E
	
	mkdir -p $(DEB_SRCBUILDS_DIR)
	mv $(TMP_DIR)`$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR)`* $(DEB_SRCBUILDS_DIR)
	
deb_binary:
	#pbuilder puts stuff in locations like this
	#/var/cache/pbuilder/testing-amd64/result/openmolar-namespace_2.0.5~2_all.deb
	
	cd $(DEB_SRCBUILDS_DIR) ; \
	sudo DIST=$(DIST) pbuilder build "`ls -r| grep .dsc -m1`" -kF230408E ;\
	mkdir -p $(DEB_BUILDS_DIR) ;\
	sudo mv $(CACHE)"`ls -r $(CACHE) | grep _all.deb -m1`" $(DEB_BUILDS_DIR)

everything:
	make all_tarballs
	make all_deb_srcs DIST=lucid DEBHELPER=py_support
	make all_deb_srcs DIST=squeeze 
	make all_deb_srcs DIST=wheezy NEW_CHANGELOG=false
	make all_deb_srcs DIST=unstable NEW_CHANGELOG=false
	make all_deb_srcs DIST=oneiric NEW_CHANGELOG=false 
	make all_deb_srcs DIST=precise NEW_CHANGELOG=false
	make all_deb_binaries DIST=lucid
	make all_deb_binaries DIST=squeeze
	make all_deb_binaries DIST=testing
	make all_deb_binaries DIST=unstable
	make all_deb_binaries DIST=oneiric
	make all_deb_binaries DIST=precise
		
test:
	@echo "chosen package $(PACKAGE)"
	@echo "targetting distro $(DIST)"
	@if [ "$(NEW_CHANGELOG)" = 'true' ]; then \
		echo "make changelog"; \
	fi
	
