#HEAD=../
HEAD=/home/neil/openmolar/hg_openmolar/
BUILD_SCRIPTS_DIR=$(HEAD)/build_scripts/

RELEASES_DIR=$(HEAD)releases/server/

TMP_DIR=$(HEAD)tmp/

DIST_DIR=$(HEAD)dist/

DEB_DIR=$(HEAD)/build_scripts/server/debian/

PACKAGE=openmolar-server

# grep setup.cnf for major versions and head revno

version=`grep 'server =' $(HEAD)setup.cnf | sed "s/.*= //"`
rev_no=`grep revision_number $(HEAD)setup.cnf | sed "s/.*= //"`

VERSION=$(version)+hg$(rev_no)

clean_tmp:
	rm -rf $(TMP_DIR)/*

sources:
	#if `hg status` then echo "uncommited changes, quitting"; exit
	cd $(HEAD) ;\
		python configure.py --server ;\
		python setup.py sdist ;\
	
	cp -av $(DIST_DIR)$(PACKAGE)-$(VERSION).tar.gz $(RELEASES_DIR)sources/
	
	cd $(RELEASES_DIR)/sources ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(PACKAGE)-$(VERSION).tar.gz ;\
	md5sum $(PACKAGE)-$(VERSION).tar.gz | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	
		
deb:
	make clean_tmp
	make sources
	
	$(BUILD_SCRIPTS_DIR)deb_maker.py -s$(RELEASES_DIR)sources -d$(DEB_DIR) -popenmolar-server
	
	cp -av $(DIST_DIR)$(PACKAGE)-$(VERSION).tar.gz $(TMP_DIR)
	gunzip $(TMP_DIR)$(PACKAGE)-$(VERSION).tar.gz
	cd $(TMP_DIR) ; tar -xvf $(TMP_DIR)$(PACKAGE)-$(VERSION).tar
	cp -av $(DEB_DIR) $(TMP_DIR)$(PACKAGE)-$(VERSION)
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; dpkg-buildpackage -kF230408E
			
	mv $(TMP_DIR)$\*.deb $(RELEASES_DIR)debs/
	
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
		

