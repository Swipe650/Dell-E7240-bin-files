#!/bin/bash

#google_home="Kitchen home"
#google_home="Bedroom mini"
#google_home="Bathroom mini"
google_home="Living Room mini"

touch ~/.lbc

if [[ -f ~/.tr ]]; then rm ~/.tr & touch ~/.lbc
fi

vol=$(/home/swipe/bin/cast-linux-amd64 --name "$google_home" status | awk -F 'Volume:' '{print $2}' | cut -c2-5)

/home/swipe/bin/cast-linux-amd64 --name "$google_home" media play http://media-ice.musicradio.com:80/LBCUK


/home/swipe/bin/cast-linux-amd64 --name "$google_home" volume $vol 
