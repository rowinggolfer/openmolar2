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
   rpm (EXPERIMENTAL!)
   
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

#in case I forget!!
ifeq ($(DIST), lucid)
	DEBHELPER=py_support
endif

ifeq ($(NEW_CHANGELOG), )
	NEW_CHANGELOG=true
endif

ifeq ($(SUFFIXES), )
	SUFFIXES = namespace common client admin server
endif

ifeq ($(DEBDISTS), )
	DEBDISTS = unstable testing stable precise lucid
endif


PACKAGE=openmolar-$(SUFFIX)

HEAD=$(HOME)/openmolar/hg_openmolar/
BUILD_SCRIPTS_DIR = $(HEAD)/build_scripts/
BUILDS_DIR=$(HEAD)builds/$(SUFFIX)/

DIST_DIR=$(HEAD)dist/

VERSION=`$(BUILD_SCRIPTS_DIR)/get_version.py $(SUFFIX)`

TARBALL = $(PACKAGE)-$(VERSION).tar.gz
TARBALL_DIR=$(HEAD)builds/$(SUFFIX)/tarballs/

TMP_DIR=$(HEAD)tmp/

###################  Debian Packaging Stuff ####################################
#                                                                              #
DEB_CONF_DIR=$(HEAD)build_scripts/$(SUFFIX)/debian_packaging/$(DEBHELPER)/debian/
DEB_BUILDS_DIR=$(BUILDS_DIR)debs/$(DIST)/

DEBHELPERS= py_support dh_python2
#                                                                              #
##################  Debian packaging ends  #####################################


##################  RPM packaging stuff    #####################################
#                                                                              #
SPEC_FILE=$(HEAD)build_scripts/$(SUFFIX)/rpm_packaging/$(PACKAGE).spec
RPM_FACTORY=$(HOME)/rpmbuild/
RPM_BUILDS_DIR=$(BUILDS_DIR)rpms/$(DIST)/
#                                                                              #
##################  RPM packaging ends     #####################################


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
	
tarballs:
	$(foreach suffix,$(SUFFIXES), \
		make SUFFIX=$(suffix) tarball \
	;)
	
sign_tarball:
	cd $(TARBALL_DIR) ;\
	gpg --armor --sign --detach-sig -u rowinggolfer@googlemail.com $(TARBALL) ;\
	md5sum $(TARBALL) | sed "s/ .*//" > $(PACKAGE)-$(VERSION)_md5.txt 	

changelog:
	# call my changelog gui
	@echo $(BUILD_SCRIPTS_DIR)deb_maker.py -s$(TARBALL_DIR) -d$(DEB_CONF_DIR) 
	$(BUILD_SCRIPTS_DIR)deb_maker.py -p$(PACKAGE) -s$(TARBALL_DIR) -d$(DEB_CONF_DIR) -popenmolar-$(SUFFIX)

deb:
	@if [ ! -e "$(TARBALL_DIR)$(TARBALL)" ]; then make tarball; fi
	
	make clean_tmp

	@echo "Making debian packages target distro = $(DIST)"
	
	# call my changelog gui if necessary
	@if [ "$(NEW_CHANGELOG)" = 'true' ]; then make changelog; fi
	
	cp -av $(TARBALL_DIR)$(TARBALL) $(TMP_DIR)
	
	mkdir -p $(DEB_BUILDS_DIR)
	
	cd $(TMP_DIR) ;\
	tar -zxvf $(TARBALL); \
	mv $(TARBALL) `$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR)`.orig.tar.gz 
	
	cd $(TMP_DIR)$(PACKAGE)-$(VERSION) ; \
	cp -av $(DEB_CONF_DIR) . ;\
	echo "modding changelog" ;\
	sed -i s/__DIST__/$(DIST)/g debian/changelog ;\
	sudo pdebuild --buildresult $(DEB_BUILDS_DIR) --pbuilderroot "sudo DIST=$(DIST)"
	
	#mv $(TMP_DIR)`$(BUILD_SCRIPTS_DIR)version_name.py $(DEB_CONF_DIR)`* $(DEB_SRCBUILDS_DIR)
	

debs:
	@echo "making all debian based packages.. first we need to update the changelogs for the 2 build systems"
	
	#make changelog DEBHELPER=<dh_python2|py_support>
	$(foreach suffix,$(SUFFIXES), \
		$(foreach var,$(DEBHELPERS), make changelog SUFFIX=$(suffix) DEBHELPER=$(var);) \
	)
	
	#make deb DIST=<unstable|testing|stable|precise|lucid> ARCH=<i386|amd64> NEW_CHANGELOG=False 
	$(foreach suffix,$(SUFFIXES), \
		$(foreach dist,$(DEBDISTS), \
			make deb SUFFIX=$(suffix) DIST=$(dist) NEW_CHANGELOG=False;) \
	)
	
	make debsigns
	
debsign:
	@echo "signing the debian packages"
	cd $(DEB_BUILDS_DIR) ;\
	debsign *.changes -kF230408E
	
debsigns:
	#make debsign DIST=<unstable|testing|stable|precise|lucid> 
	
	$(foreach suffix,$(SUFFIXES), \
		$(foreach dist,$(DEBDISTS), \
			make debsign SUFFIX=$(suffix) DIST=$(dist) ;) \
		) 

pushdebs:
	@echo "updating the local repo"
	$(foreach suffix,$(SUFFIXES), \
		$(foreach dist,$(DEBDISTS), \
			cd ~/www/repos/apt/debian ;\
			reprepro include $(dist) $(HEAD)builds/$(suffix)/debs/$(dist)/*.changes ; \
		) \
	 )
	
	#reprepro includedeb squeeze $(RELEASE_DIR)namespace/debs/*.deb ;\
	#reprepro includedeb squeeze $(RELEASE_DIR)client/debs/*.deb ;\
	#reprepro includedeb squeeze $(RELEASE_DIR)common/debs/*.deb ;\
	#reprepro includedeb squeeze $(RELEASE_DIR)admin/debs/*.deb ;\
	#reprepro includedeb squeeze $(RELEASE_DIR)server/debs/*.deb

rpm:
	@if [ ! -e "$(TARBALL_DIR)$(TARBALL)" ]; then make tarball; fi
	
	@echo "target distro = $(DIST)"
	rpmdev-setuptree
	
	#cp -av $(SPEC_FILE) $(RPM_FACTORY)
	cp -av $(TARBALL_DIR)$(TARBALL) $(RPM_FACTORY)SOURCES/
	cp -av $(SPEC_FILE) $(RPM_FACTORY)SPECS/
	# make the rpm here!
	rpmbuild -ba $(SPEC_FILE)
	
	mkdir -p $(RPM_BUILDS_DIR)
	touch $(RPM_BUILDS_DIR)rpm_result
	
	
	
test:
	@echo "chosen package $(PACKAGE)"
	@echo "targetting distro $(DIST)"
	@if [ "$(NEW_CHANGELOG)" = 'true' ]; then \
		echo "will prompt for new changelog"; \
	fi
	@echo "debconfdir = $(DEB_CONF_DIR)"
	@echo "Dist = $(DIST)"
	
