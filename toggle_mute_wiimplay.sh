#!/bin/bash

get_vol=$(playerctl -p wiimplay volume)

vol=$get_vol

mute () { playerctl -p wiimplay volume 0 ; }


unmute () { playerctl -p wiimplay volume "$vol" ; }


set_default_mute_time()
{
    mute

    sleep 210

    unmute
}


check_top_of_the_hour()
{
# Get current time in minutes
    currenttime=$(date +%M)

# check time for Talkradio
    st=$(playerctl -p wiimplay metadata title)
    talkradio='Talk Radio'
    case "$st" in
    "$talkradio" )

#     if [ "$currenttime" -eq "58" ] || [ "$currenttime" -eq "59" ]  || [ "$currenttime" -eq "00" ] || [ "$currenttime" -eq "01" ] || [ "$currenttime" -eq "02" ] || [ "$currenttime" -eq "03" ]  || [ "$currenttime" -eq "04" ]; then
#
#     mute
#
#     sleep 30
#
#     unmute
#
#     fi

    if [ "$currenttime" -gt "00" ] && [ "$currenttime" -lt "07" ]; then

    mute

    sleep 60

    unmute

    else

    set_default_mute_time

    fi

    esac


    # check time for lbc
    st=$(playerctl -p wiimplay metadata title)
    lbc='LBC UK'
    case "$st" in
    "$lbc" )

    if [ "$currenttime" -gt "00" ] && [ "$currenttime" -lt "07" ]; then
#
    mute

    sleep 30

    unmute

    else

    set_default_mute_time

    fi

    esac
}

check_top_of_the_hour
