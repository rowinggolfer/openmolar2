SUFFIX=namespace
PACKAGE=openmolar-$(SUFFIX)

ifeq ($(DIST), )
	DIST=unstable
endif


HEAD=$(HOME)/openmolar/hg_openmolar/
BUILD_SCRIPTS_DIR = $(HEAD)/build_scripts/
BUILDS_DIR=$(HEAD)builds/$(SUFFIX)/

DIST_DIR=$(HEAD)dist/
DEB_CONF_DIR=$(HEAD)build_scripts/$(SUFFIX)/metadata/$(DIST)/debian/

VERSION=`$(BUILD_SCRIPTS_DIR)/get_version.py $(SUFFIX)`

TARBALL = $(PACKAGE)-$(VERSION).tar.gz
TARBALL_DIR=$(HEAD)builds/$(SUFFIX)/tarballs/

TMP_DIR=$(HEAD)tmp/

DEB_SRCBUILDS_DIR=$(BUILDS_DIR)deb_srcs/$(DIST)/
DEB_BUILDS_DIR=$(BUILDS_DIR)debs/$(DIST)/


#this is where pbuilder puts stuff
CACHE=/var/cache/pbuilder/$(DIST)-amd64/result/

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
	
sign_tarball:
	cd $(TARBALL_DIR) ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(TARBALL) ;\
	md5sum $(TARBALL) | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	
	
	
deb_src:
	make tarball
	make clean_tmp

	@echo "target distro = $(DIST)"
	
	# call my changelog gui	
	$(BUILD_SCRIPTS_DIR)deb_maker.py -s$(TARBALL_DIR) -d$(DEB_CONF_DIR) -popenmolar-$(SUFFIX)
	
	cp -av $(TARBALL_DIR)$(TARBALL) $(TMP_DIR)
	
	cd $(TMP_DIR) ;\
	tar -zxvf $(TARBALL); \
	mv $(TARBALL) `$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR)`.orig.tar.gz 
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; \
	cp -av $(DEB_CONF_DIR) . ;\
	dpkg-buildpackage -S -kF230408E
	
	mkdir -p $(DEB_SRCBUILDS_DIR)
	mv $(TMP_DIR)`$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR)`* $(DEB_SRCBUILDS_DIR)
	
debs:
	cd $(DEB_SRCBUILDS_DIR) ; \
	sudo DIST=$(DIST) pbuilder build `$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR) full`.dsc -kF230408E
			
	mkdir -p $(DEB_BUILDS_DIR)
	
	#pbuilder puts stuff in locations like this
	#/var/cache/pbuilder/testing-amd64/result/openmolar-namespace_2.0.5~2_all.deb
	sudo mv $(CACHE)`$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR) full`_all.deb $(DEB_BUILDS_DIR)
		

test:
	@echo "targetting $(DIST)"
