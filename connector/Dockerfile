FROM alpine:edge

RUN apk add --no-cache coreutils nmap-ncat

EXPOSE 2560/tcp

SHELL ["/bin/ash", "-c"]
CMD stty -F /dev/arduino -echo 115200 && \
    ncat -n -k -l 2560 </dev/arduino >/dev/arduino
