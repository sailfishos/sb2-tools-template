#!/bin/sh
ARCHS="armv6l armv7l armv7hl mipsel"

echo -n "arch i586 targets " > baselibs.conf
for x in $ARCHS; do
	cp -v sb2-tools-template-rpmlintrc sb2-tools-$x-rpmlintrc
	sed "s/@ARCH@/$x/g" sb2-tools-template.spec | sed "s/ExclusiveArch: nothing/ExclusiveArch: %{ix86}/g" > sb2-tools-$x.spec	
	echo -n "$x:inject " >> baselibs.conf
done