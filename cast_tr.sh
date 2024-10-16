#!/bin/bash

google_home="Kitchen home"
#google_home="Bedroom mini"
#google_home="Bathroom mini"

touch ~/.tr

if [[ -f ~/.lbc ]]; then rm ~/.lbc & touch ~/.tr
fi

vol=$(/home/swipe/bin/cast-linux-amd64 --name "$google_home" status | awk -F 'Volume:' '{print $2}' | cut -c2-5)

/home/swipe/bin/cast-linux-amd64 --name "$google_home" media play http://radio.talkradio.co.uk/stream?

/home/swipe/bin/cast-linux-amd64 --name "$google_home" volume $vol
