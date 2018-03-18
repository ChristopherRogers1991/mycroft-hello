#!/bin/bash

sudo apt-get install python-opencv

if [[ $VIRTUAL_ENV != "" ]]; then
    ln -s /usr/lib/python2.7/dist-packages/cv2.x86_64-linux-gnu.so $VIRTUAL_ENV/lib/python2.7/site-packages/
fi
