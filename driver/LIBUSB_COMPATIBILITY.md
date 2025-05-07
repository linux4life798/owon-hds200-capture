# Using Libusb Utilities/Libraries with OWON Devices

Linux kernel [OWON oscilloscope support](https://github.com/torvalds/linux/commit/4cc01410e1c1dd075df10f750775c81d1cb6672b) landed upstream in the usb-serial-simple kernel driver
on April 25, 2025 in [this merge](https://github.com/torvalds/linux/commit/2d5c7fe09739d49612e69ad61ced0a0f19651769).
This means that you can now interface with OWON devices over a simple serial
interface, say /dev/ttyUSB0 ([example](identify.py)), rather than raw libusb. Although this is a win for
new libraries, existing OWON utilities/libraries may still use libusb.

**If you are using one of these OWON tools/libraries and are seeing an error
similar to "device is busy or in use", the following help guide is for you.**

## For Users

Please file a bug with the software maintainer and point them to this document
to correct the behavior in code. In the meantime, here are some workarounds:

<details>
<summary>Simple</summary>

```bash
sudo modprobe -r usb_serial_simple
```

This will cause usb_serial_simple to unbind from all devices it supports,
including OWON devices. You can then use the utility/library as normal.
Your machine will go back to normal after a reboot or an explicit
`sudo modprobe usb_serial_simple`.

</details>

<details>
<summary>More Targeted</summary>

If you still need usb_serial_simple to service other non-owon devices, but
want to simply unbind it from an owon device, you can do something like
following:

```bash
me@owon-test:~$ sudo dmesg
[ 3123.753974] usb 1-3: new full-speed USB device number 4 using xhci_hcd
[ 3124.001211] usb 1-3: New USB device found, idVendor=5345, idProduct=1234, bcdDevice= 1.00
[ 3124.001219] usb 1-3: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[ 3124.001221] usb 1-3: Product: oscilloscope
[ 3124.001223] usb 1-3: Manufacturer: oscilloscope
[ 3124.001224] usb 1-3: SerialNumber: oscilloscope
[ 3124.002024] usb_serial_simple 1-3:1.0: owon converter detected
[ 3124.002143] usb 1-3: owon converter now attached to ttyUSB0
# Note the usb bus device identifier "1-3:1.0".

me@owon-test:~$ ls -al /sys/bus/usb/drivers/usb_serial_simple/
total 0
drwxr-xr-x 2 root root    0 May  6 18:38 .
drwxr-xr-x 8 root root    0 May  6 18:38 ..
lrwxrwxrwx 1 root root    0 May  6 18:38 1-3:1.0 -> ../../../../devices/pci0000:00/0000:00:02.1/0000:02:00.0/usb1/1-3/1-3:1.0
--w------- 1 root root 4096 May  6 18:38 bind
lrwxrwxrwx 1 root root    0 May  6 18:38 module -> ../../../../module/usbserial
--w------- 1 root root 4096 May  6 18:38 uevent
--w------- 1 root root 4096 May  6 18:38 unbind
# We can confirm that the device "1-3:1.0" was bound.

# Force usb_serial_simple to unbind from this specific device.
me@owon-test:~$ echo '1-3:1.0' | sudo tee /sys/bus/usb/drivers/usb_serial_simple/unbind
1-3:1.0

# The "1-3:1.0" device is gone.

me@owon-test:~$ sudo dmesg
[ 3123.753974] usb 1-3: new full-speed USB device number 4 using xhci_hcd
[ 3124.001211] usb 1-3: New USB device found, idVendor=5345, idProduct=1234, bcdDevice= 1.00
[ 3124.001219] usb 1-3: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[ 3124.001221] usb 1-3: Product: oscilloscope
[ 3124.001223] usb 1-3: Manufacturer: oscilloscope
[ 3124.001224] usb 1-3: SerialNumber: oscilloscope
[ 3124.002024] usb_serial_simple 1-3:1.0: owon converter detected
[ 3124.002143] usb 1-3: owon converter now attached to ttyUSB0
[ 3233.173129] owon ttyUSB0: owon converter now disconnected from ttyUSB0
[ 3233.173155] usb_serial_simple 1-3:1.0: device disconnected
# Observe the disconnects.
```

</details>

## For Library/Utility Maintainers

Please use libusb's kernel driver management functions to detach the kernel
driver before claiming the interface and reattach the kernel driver before
exiting.

Libusb Kernel Driver Management Functions:
* [`libusb_set_auto_detach_kernel_driver`](https://libusb.sourceforge.io/api-1.0/group__libusb__dev.html#gac35b26fef01271eba65c60b2b3ce1cbf) - Enable a mechanism to automatically detach the kernel driver on an interface when claiming the interface, and attach it when releasing the interface.
* [`libusb_kernel_driver_active`](https://libusb.sourceforge.io/api-1.0/group__libusb__dev.html#ga1cabd4660a274f715eeb82de112e0779) - Check if a kernel driver is active on the interface.
* [`libusb_detach_kernel_driver`](https://libusb.sourceforge.io/api-1.0/group__libusb__dev.html#ga5e0cc1d666097e915748593effdc634a) - Detach the kernel driver.
* [`libusb_attach_kernel_driver`](https://libusb.sourceforge.io/api-1.0/group__libusb__dev.html#gadeba36e900db663c0b7cf1b164a20d02) - Reatach the kernel driver.

See the additional language specific help:

<details>
<summary>C</summary>

You can use the [`libusb_set_auto_detach_kernel_driver`](https://libusb.sourceforge.io/api-1.0/group__libusb__dev.html#gac35b26fef01271eba65c60b2b3ce1cbf) function to automatically detach and reattach the kernel driver.

```c
device = libusb_open_device_with_vid_pid(NULL, 0x5345, 0x1234);
/*...*/
/* We need to claim the first interface */
libusb_set_auto_detach_kernel_driver(device, 1);
libusb_claim_interface(device, 0)
/*...*/
```

Example:
https://github.com/libusb/libusb/blob/9cef804b2454a2226f5fa5db79a7e9aa8a45d4d4/examples/fxload.c#L253-L255

</details>

<details>
<summary>Python</summary>

This assumes you are using [pyusb](https://pypi.org/project/pyusb/).
Unfortunately, it doesn't support the automatic detach and reattach, so you need to do something like the following:

```python
usb_device = usb.core.find(idVendor=0x5345, idProduct=0x1234)
reattach = False

# ...
# Detach kernel driver if active.
if usb_device.is_kernel_driver_active(0):
    reattach = True
    usb_device.detach_kernel_driver(0)

# claim and configure ...

# Closing:
if reattach:
    usb_device.attach_kernel_driver(0)
```

These functions are implemented [here](https://github.com/pyusb/pyusb/blob/c384631d0aee97f78fa2478e8836a6a17f3ea9c7/usb/core.py#L1110-L1146).
</details>
