# AVR Simulator

`qemu-system-avr` tries to use all the CPU cicles (leaving a CPU core stuck at 100%. Limit CPU core usage to 10%. I may be adjusted on slower machines.

```bash
$ podman build -t dcc/net-to-serial:sim . 
$ podman run --init --cpu 0.1 -d -p 2560:2560 dcc/net-to-serial:sim
```