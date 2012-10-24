Installation on Ubuntu
======================

:Author: Neil Wallace neil@openmolar.com

Debian is my Gnu/linux distribution of choice, and the platform I have used for 
the majority of time whilst developing openmolar2.

However in recognition of the popularity of the Ubuntu distribution, I regularly
build for their LTS versions also.

Ubuntu repos ::
	
	LUCID (10.04)
	deb http://openmolar.com/ubuntu lucid main
	deb-src http://openmolar.com/ubuntu lucid main
	
	PRECISE (12.10)
	deb http://openmolar.com/ubuntu precise main
	deb-src http://openmolar.com/ubuntu precise main
	
	QUANTAL (12.14)
	deb http://openmolar.com/ubuntu quantal main
	deb-src http://openmolar.com/ubuntu quantal main

add the flavuor you require to your sources.list 

The repo is signed by my key, which is available ::

	http://www.openmolar.com/rowinggolfer.gpg.key
	

Once you have enabled the repo of your choice, get whichever components you require. ::
	
	OPENMOLAR2
	~# apt-get install openmolar-server openmolar-admin openmolar-client
	
	OPENMOLAR1 (deprecated)
	~# apt-get install openmolar-orig

