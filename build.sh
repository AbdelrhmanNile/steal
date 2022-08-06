#!/usr/bin/tcsh

set APP_NAME="steal"

# setup output
set OUTPUT="${APP_NAME}"
if $#argv > 0 then
    set OUTPUT=$argv[1]
endif
echo "output will be to $OUTPUT"

# copy initial part of shell script into output file
cp ${APP_NAME}.basis $OUTPUT

# create a tar file of the Hand And Foot app
rm -f tmp.tar
tar cf steal.tar *.py

# add the uuencoded version of the app to the end of the output file
uuencode steal.tar steal.tar >> $OUTPUT
chmod 755 $OUTPUT

# How does a file named "0" get created?? Don't know, but this gets rid of it
rm -f 0
