# OWON Models + FW and USB Descriptors

* https://usb-ids.gowdy.us/read/UD/5345/1234
* https://bugzilla.kernel.org/show_bug.cgi?id=220193
* https://lore.kernel.org/linux-usb/20260810091322.2201740-1-huangwei@kylinos.cn/

## Inquiries

* https://github.com/lucky62/OWON_SDS1102_Linux_Capture/issues/1
* https://github.com/mjkloeckner/TB066/issues/1
* https://github.com/JohnDWilbourn/owon-hds200/issues/1
* https://github.com/einsz/whoop_thrust_stand/issues/1
* https://github.com/mkreutner/hds-mirror/issues/1
* https://github.com/scottsun2020/owon-electronic-load-tests/issues/1

## HDS200

<img width="128" src="https://github.com/user-attachments/assets/f7622632-6d8e-43e9-9a86-9d0ee88e8155" />


<details>
  <summary>OWON HDS272S running firmware V5.7.1 checksum d5e97f14</summary>

```
Bus 005 Device 012: ID 5345:1234 Owon PDS6062T Oscilloscope
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
</details>

<details>
  <summary>OWON HDS272S running firmware V5.6.2 checksum 1367da05</summary>

```
Bus 005 Device 011: ID 5345:1234 Owon PDS6062T Oscilloscope
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
</details>


## SDS1102

<img width="128" src="https://github.com/user-attachments/assets/ef60a36d-9931-499b-a439-3bea4018a3e9" />

<details>
  <summary>@lucky62's OWON SDS1102 running firmware V4.0.1</summary>

From https://github.com/lucky62/OWON_SDS1102_Linux_Capture/issues/1

```
Bus 003 Device 015: ID 5345:1234 Owon PDS6062T Oscilloscope
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
  bcdDevice            2.94
  iManufacturer           1 System CPU
  iProduct                2 Oscilloscope
  iSerial                 3 SERIAL
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x0020
    bNumInterfaces          1
    bConfigurationValue     1
    iConfiguration          5 
    bmAttributes         0xc0
      Self Powered
    MaxPower              500mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           2
      bInterfaceClass         5 Physical Interface Device
      bInterfaceSubClass      6 [unknown]
      bInterfaceProtocol     80 
      iInterface              4 
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0200  1x 512 bytes
        bInterval               0
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x03  EP 3 OUT
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0200  1x 512 bytes
        bInterval               0
```
</details>

## VDS1022

<img width="128" src="https://github.com/user-attachments/assets/adeda226-dcf3-4798-8241-ff53160da046" />


<details>
  <summary>@leStoppe's OWON VDS1022</summary>

From https://bugzilla.kernel.org/show_bug.cgi?id=220193#c6

```
Bus 001 Device 003: ID 5345:1234 Owon PDS6062T Oscilloscope
Negotiated speed: Full Speed (12Mbps)
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               2.00
  bDeviceClass            2 Communications
  bDeviceSubClass         0 [unknown]
  bDeviceProtocol         0 
  bMaxPacketSize0        64
  idVendor           0x5345 Owon
  idProduct          0x1234 PDS6062T Oscilloscope
  bcdDevice           10.01
  iManufacturer           1 S
  iProduct                2 U
  iSerial                 3 0
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x0029
    bNumInterfaces          1
    bConfigurationValue     1
    iConfiguration          0 
    bmAttributes         0xc0
      Self Powered
    MaxPower               50mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           2
      bInterfaceClass         5 Physical Interface Device
      bInterfaceSubClass      6 [unknown]
      bInterfaceProtocol     80 
      iInterface              0 
      ** UNRECOGNIZED:  09 21 00 01 00 01 22 00 00
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               0
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x03  EP 3 OUT
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               0
cannot read device status, Resource temporarily unavailable (11)
```
</details>

<details>
  <summary>@vfperri88's OWON VDS1022I</summary>

From https://github.com/florentbr/OWON-VDS1022/issues/54#issuecomment-1120191539

Board version `4.0.0` from https://github.com/florentbr/OWON-VDS1022/issues/54#issuecomment-1120242373 .

```
Bus 001 Device 004: ID 5345:1234 Owon PDS6062T Oscilloscope
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               2.00
  bDeviceClass            0
  bDeviceSubClass         0
  bDeviceProtocol         0
  bMaxPacketSize0        64
  idVendor           0x5345 Owon
  idProduct          0x1234 PDS6062T Oscilloscope
  bcdDevice            1.00
  iManufacturer           1 ZHBI2.0
  iProduct                2 ZPRO2.0
  iSerial                 3 VDS1022
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
      bInterfaceSubClass      0
      bInterfaceProtocol      0
      iInterface              0
      ** UNRECOGNIZED: 09 21 11 01 00 01 22 5f 00
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81 EP 1 IN
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040 1x 64 bytes
        bInterval              32
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x01 EP 1 OUT
        bmAttributes            2
          Transfer Type            Bulk
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040 1x 64 bytes
        bInterval              32
can't get device qualifier: Resource temporarily unavailable
can't get debug descriptor: Resource temporarily unavailable
Device Status: 0x0000
  (Bus Powered)
```
</details>
