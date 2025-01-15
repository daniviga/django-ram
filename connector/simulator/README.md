# Connector and AVR simulator

> [!WARNING]
> The simulator is intended for light development and testing purposes only and far from being a complete replacement for a real hardware.

`qemu-system-avr` tries to use all the CPU cycles (leaving a CPU core stuck at 100%; limit CPU core usage to 10% via `--cpus 0.1`. It can be adjusted on slower machines.

```bash
$ podman build -t dcc/connector:sim .
$ podman run --init --cpus 0.1 -d -p 2560:2560 dcc/connector:sim
```

All traffic will be collected on the container's `stderr` for debugging purposes.
