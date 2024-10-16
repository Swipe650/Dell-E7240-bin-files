#!/bin/bash

vol=$(playerctl -p wiimplay volume | cut -c4-5 | bc -l)

    if [[ "$vol" -eq "00" ]]; then
      playerctl -p wiimplay volume 0.26
      
      
    elif [[ "$vol" -gt "01" ]]; then
      playerctl -p wiimplay volume 0
    fi 
