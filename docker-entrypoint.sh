#!/bin/bash

if [[ -d /media/secrets ]]; then
	for i in $(ls /media/secrets); do
		export $(echo $i | tr '[a-z-]' '[A-Z_]')=$(cat /media/secrets/$i)
	done
fi

exec "$@"
