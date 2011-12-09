#if `hg status` then echo "uncommited changes, quitting"; exit	

HOME=/home/neil/


server_sources:
	cd server ; make sources
		
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
	cd $(HOME)www/repos/apt/debian/ ;\
	reprepro includedeb squeeze $(HOME)openmolar/hg_openmolar/releases/namespace/debs/*.deb ;\
	reprepro includedeb squeeze $(HOME)openmolar/hg_openmolar/releases/client/debs/*.deb ;\
	reprepro includedeb squeeze $(HOME)openmolar/hg_openmolar/releases/common/debs/*.deb ;\
	reprepro includedeb squeeze $(HOME)openmolar/hg_openmolar/releases/admin/debs/*.deb ;\
	reprepro includedeb squeeze $(HOME)openmolar/hg_openmolar/releases/server/debs/*.deb
	

all:
	make namespace_deb
	make common_deb
	make admin_deb
	make client_deb
	make server_deb
