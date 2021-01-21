#!/bin/sh
ARCHS="armv7hl aarch64 i486"

for x in $ARCHS; do
	sed "s/@ARCH@/$x/g" sb2-tools-template.spec > sb2-tools-$x.spec
done
