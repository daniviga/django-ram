FROM alpine:edge

RUN apk update && apk add nmap-ncat

EXPOSE 2560/tcp

CMD ncat -n -k -l 2560 </dev/arduino >/dev/arduino
