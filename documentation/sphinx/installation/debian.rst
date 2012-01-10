Installation on Debian
======================

:Author: Neil Wallace neil@openmolar.com
   
Debian is my Gnu/linux distribution of choice, and the platform I have used for 
the majority of time whilst developing openmolar2.

Consequently, it should come as no surprise that installation on this platform
is well supported (and hopefully painless!).

In fact, the following should get be all you require to do.

 1. Add my repo and key. ::
 
    ~# echo "deb http://openmolar.com/repos/apt/debian squeeze main" >> /etc/apt/sources.list
    ~# wget -O - http://www.openmolar.com/rowinggolfer.gpg.key| apt-key add -

 2. update. ::
 
    ~# apt-get update

 3. Get whichever components you require. ::
 
    ~# apt-get install openmolar-server openmolar-admin openmolar-client
 
