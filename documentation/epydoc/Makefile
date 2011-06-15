#MakeFile

clean:
	rm -rf html

doc:	
	epydoc --separate-classes -v -o html ../../lib_openmolar

publish:
	rsync -av html/ amazon:rg_website/openmolar2/epydoc/
