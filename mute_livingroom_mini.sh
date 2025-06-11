sleep-with-countdown() {
  cast-linux-amd64 --name "Living Room mini" volume 0
  secs=$1
  while [ $secs -gt 0 ]; do
    printf "\rsleep: $secs\033[0K"
    sleep 1
    : $((secs--))
  done
  printf "\n"
  cast-linux-amd64 --name "Living Room mini" volume 0.45
}

sleep-with-countdown $1

