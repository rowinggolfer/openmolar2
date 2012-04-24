Installation on Ubuntu
======================

:Author: Neil Wallace neil@openmolar.com
   
Debian is my Gnu/linux distribution of choice, and the platform I have used for 
the majority of time whilst developing openmolar2.

However in recognition of the popularity of the Ubuntu distribution, I regularly
build for their LTS versions also.

Ubuntu repos ::

	deb http://openmolar.com/ubuntu lucid main
	deb http://openmolar.com/ubuntu precise main
	
add the flavuor you require to your sources.list 

The repo is signed by my key, which is available ::

	http://www.openmolar.com/rowinggolfer.gpg.key
	

Once you have enabled the repo of your choice, get whichever components you require. ::
 
    ~# apt-get install openmolar-server openmolar-admin openmolar-client
 
