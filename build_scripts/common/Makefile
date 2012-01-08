HEAD=$(HOME)/openmolar/hg_openmolar/
BUILD_SCRIPTS_DIR=$(HEAD)/build_scripts/

SUFFIX=common

RELEASES_DIR=$(HEAD)releases/$(SUFFIX)/

TMP_DIR=$(HEAD)tmp/

DIST_DIR=$(HEAD)dist/

DEB_DIR=$(HEAD)/build_scripts/$(SUFFIX)/debian/

PACKAGE=openmolar-$(SUFFIX)

VERSION=`$(BUILD_SCRIPTS_DIR)/get_version.py $(SUFFIX)`

clean_tmp:
	rm -rf $(TMP_DIR)/*

sources:
	cd $(HEAD) ;\
		python configure.py --$(SUFFIX) ;\
		python setup.py sdist ;\
	
	cp -av $(DIST_DIR)$(PACKAGE)-$(VERSION).tar.gz $(RELEASES_DIR)sources/
	
	cd $(RELEASES_DIR)/sources ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(PACKAGE)-$(VERSION).tar.gz ;\
	md5sum $(PACKAGE)-$(VERSION).tar.gz | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	
		
deb:
	make clean_tmp
	make sources
	
	$(BUILD_SCRIPTS_DIR)deb_maker.py -s$(RELEASES_DIR)sources -d$(DEB_DIR) -popenmolar-$(SUFFIX)
	
	cp -av $(DIST_DIR)$(PACKAGE)-$(VERSION).tar.gz $(TMP_DIR)
	gunzip $(TMP_DIR)$(PACKAGE)-$(VERSION).tar.gz
	cd $(TMP_DIR) ; tar -xvf $(TMP_DIR)$(PACKAGE)-$(VERSION).tar
	cp -av $(DEB_DIR) $(TMP_DIR)$(PACKAGE)-$(VERSION)
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; dpkg-buildpackage -kF230408E
			
	mv $(TMP_DIR)$\*.deb $(RELEASES_DIR)debs/
	
	make clean_tmp
	
