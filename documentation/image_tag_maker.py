#! /usr/bin/env python

import os

basestr = \
'''            <mediaobject>
                <imageobject>
                    <imagedata fileref="images/screenshots/PATH" format="PNG" />
                </imageobject>
            </mediaobject>
'''


images = os.listdir("images/screenshots/")
images.sort()
for image in images:

    print basestr.replace("PATH", image)


