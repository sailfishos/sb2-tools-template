#!/bin/sh
ARCHS="armv6l armv7l armv7hl armv7thl armv7tnhl mipsel aarch64 i486"

for x in $ARCHS; do
	sed "s/@ARCH@/$x/g" sb2-tools-template.spec > sb2-tools-$x.spec
done
