#MakeFile

clean:
	echo "removing the pdf and html folders"
	rm -rf pdf
	rm -rf html
    
check:
	jing /usr/share/xml/docbook/schema/rng/5.0/docbook.rng openmolar2.docbook
    
pdf:
	xsltproc -o pdf/tmp.fo /usr/share/xml/docbook/stylesheet/docbook-xsl/fo/docbook.xsl openmolar2.docbook 
	fop pdf/tmp.fo pdf/openmolar2.pdf
	rm pdf/tmp.fo
    
html:
	xsltproc -o html/ /usr/share/xml/docbook/stylesheet/docbook-xsl/html/chunk.xsl openmolar2.docbook
	cp -a images/ html/


publish:
	echo "publishing html version"
	rsync -av html/ amazon:rg_website/openmolar2/docbook/
	echo "publishing pdf version"
	rsync -av pdf/ amazon:rg_website/openmolar2/docbook
