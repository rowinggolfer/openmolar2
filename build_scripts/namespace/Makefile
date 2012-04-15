HEAD=$(HOME)/openmolar/hg_openmolar/
BUILD_SCRIPTS_DIR=$(HEAD)/build_scripts/

SUFFIX=namespace

RELEASES_DIR=$(HEAD)releases/$(SUFFIX)/

TMP_DIR=$(HEAD)tmp/

DIST_DIR=$(HEAD)dist/

DEB_DIR=$(HEAD)/build_scripts/$(SUFFIX)/debian/

PACKAGE=openmolar-$(SUFFIX)

VERSION=`$(BUILD_SCRIPTS_DIR)/get_version.py $(SUFFIX)`

clean_tmp:
	mkdir -p $(TMP_DIR)
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
	make sources
	make clean_tmp
	
	$(BUILD_SCRIPTS_DIR)deb_maker.py -s$(RELEASES_DIR)sources -d$(DEB_DIR) -popenmolar-$(SUFFIX)
	
	cp -av $(DIST_DIR)$(PACKAGE)-$(VERSION).tar.gz $(TMP_DIR)
	cp -av $(DIST_DIR)$(PACKAGE)-$(VERSION).tar.gz $(TMP_DIR)$(PACKAGE)-$(VERSION).orig.tar.gz
	gunzip $(TMP_DIR)$(PACKAGE)-$(VERSION).tar.gz
	cd $(TMP_DIR) ; tar -xvf $(TMP_DIR)$(PACKAGE)-$(VERSION).tar
	cp -av $(DEB_DIR) $(TMP_DIR)$(PACKAGE)-$(VERSION)
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; \dpkg-buildpackage -S -kF230408E
	#cd $(TMP_DIR)$ ; sudo pbuilder build $(PACKAGE)_$(VERSION)~6.dsc
			
	#mv $(TMP_DIR)$\*.deb $(RELEASES_DIR)debs/
	
	#make clean_tmp
	
