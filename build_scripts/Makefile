#if `hg status` then echo "uncommited changes, quitting"; exit	

RELEASE_DIR = $(dir $(realpath .))releases/

REPO_DIR = $(HOME)/www/repos/apt/debian/
	
server_sources:
	cd server ; 
ifeq (`hg status`,)
	make sources
else
	@echo "unable to build server sources you have uncommitted changes"
endif
		
server_deb:
	cd server ; make deb
		
admin_sources:
	cd admin ; make sources
		
admin_deb:
	cd admin ; make deb

common_sources:
	cd common ; make sources
		
common_deb:
	cd common ; make deb

client_sources:
	cd client ; make sources
		
client_deb:
	cd client ; make deb
	
namespace_sources:
	cd namespace ; make sources
		
namespace_deb:
	cd namespace ; make deb
	
pushdebs:
	cd $(REPO_DIR) ;\
	reprepro includedeb squeeze $(RELEASE_DIR)namespace/debs/*.deb ;\
	reprepro includedeb squeeze $(RELEASE_DIR)client/debs/*.deb ;\
	reprepro includedeb squeeze $(RELEASE_DIR)common/debs/*.deb ;\
	reprepro includedeb squeeze $(RELEASE_DIR)admin/debs/*.deb ;\
	reprepro includedeb squeeze $(RELEASE_DIR)server/debs/*.deb
	

all:
	#make namespace_deb
	echo "WARNING - not making new namespace_deb"
	make common_deb
	make admin_deb
	make client_deb
	make server_deb
