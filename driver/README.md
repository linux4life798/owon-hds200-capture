# Linux Kernel Serial Driver
**Not required for library to function.**

This introduces a standalone Linux kernel driver for OWON oscilloscopes.

It's role is to simply associate a serial interface with the oscilloscope's
IN/OUT USB endpoints, in teh most generic way possible.


## Testing and Usage

```bash
sudo apt install build-essential linux-headers-amd64
make
sudo insmod owon.ko
echo "module usbserial +p" | sudo tee /sys/kernel/debug/dynamic_debug/control
# Plug in device.
sudo chown $USER /dev/ttyUSB0
# Disable echo (wireshark sees it echoing data from the device back to the device)
# Disable line ending modification.
stty -F /dev/ttyUSB0 -echo raw
echo "*IDN?" >/dev/ttyUSB0
timeout 1 cat /dev/ttyUSB0
```

## USB Info

```
Bus 001 Device 019: ID 5345:1234 Owon PDS6062T Oscilloscope
Negotiated speed: Full Speed (12Mbps)
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               2.00
  bDeviceClass            0 [unknown]
  bDeviceSubClass         0 [unknown]
  bDeviceProtocol         0
  bMaxPacketSize0        64
  idVendor           0x5345 Owon
  idProduct          0x1234 PDS6062T Oscilloscope
  bcdDevice            1.00
  iManufacturer           1 oscilloscope
  iProduct                2 oscilloscope
  iSerial                 3 oscilloscope
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x0029
    bNumInterfaces          1
    bConfigurationValue     1
    iConfiguration          0
    bmAttributes         0x80
      (Bus Powered)
    MaxPower              100mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           2
      bInterfaceClass         5 Physical Interface Device
      bInterfaceSubClass      0 [unknown]
      bInterfaceProtocol      0
      iInterface              0
      ** UNRECOGNIZED:  09 21 11 01 00 01 22 5f 00
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval              32
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x01  EP 1 OUT
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval              32
Device Status:     0x0000
  (Bus Powered)
```
