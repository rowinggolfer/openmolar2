#HEAD=../
HEAD=/home/neil/openmolar/hg_openmolar/

RELEASES_DIR=$(HEAD)releases/server/

TMP_DIR=$(HEAD)tmp/

DIST_DIR=$(HEAD)dist/

DEB_DIR=$(HEAD)/build_scripts/server/debian/

PACKAGE=openmolar-server

VERSION=2.0.0+hg79

DEB_NO = 0

clean_tmp:
	rm -rf $(TMP_DIR)/*

sources:
	#if `hg status` then echo "uncommited changes, quitting"; exit
	cd $(HEAD) ;\
		python configure.py --server ;\
		python setup.py sdist ;\
	
	cp -av $(DIST_DIR)$(PACKAGE)-$(VERSION).tar.gz $(RELEASES_DIR)tarballs/
	
	cd $(RELEASES_DIR)/tarballs ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(PACKAGE)-$(VERSION).tar.gz ;\
	md5sum $(PACKAGE)-$(VERSION).tar.gz | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	
		
deb:
	#python new_changelog.py $(VERSION) $(PACKAGING_NO) > $(VERSIONED_TMP_DIR)debian/changelog
	
	make clean_tmp
	make sources
	
	cp -av $(DIST_DIR)$(PACKAGE)-$(VERSION).tar.gz $(TMP_DIR)
	gunzip $(TMP_DIR)$(PACKAGE)-$(VERSION).tar.gz
	cd $(TMP_DIR) ; tar -xvf $(TMP_DIR)$(PACKAGE)-$(VERSION).tar
	cp -av $(DEB_DIR) $(TMP_DIR)$(PACKAGE)-$(VERSION)
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; dpkg-buildpackage -kF230408E
			
	mv $(TMP_DIR)$(PACKAGE)_$(VERSION)~$(DEB_NO)_all.deb $(RELEASES_DIR)debs/
	
	#mv $(VERSIONED_TMP_DIR)debian/changelog $(TEMPLATES_DIR)changelog_history.txt
	make clean_tmp
	
rpm:
	
	cd $(TMP_DIR);\
		python setup.py bdist_rpm --release $(PACKAGING_NO)
		rpm --addsign $(TMP_DIR)dist/auteur-$(VERSION)-$(PACKAGING_NO).noarch.rpm
		
	mv $(TMP_DIR)dist/auteur-$(VERSION)-$(PACKAGING_NO).noarch.rpm $(RELEASES_DIR)rpm/ 
	
all:
	make source_tarball
	make rpm
	make deb
	@echo "drop into arch VM and type make au"
		

