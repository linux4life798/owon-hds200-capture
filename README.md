# OWON HDS200 Series Oscilloscope Capture Tool

## Usage

* The core USB SCPI interface library, [owon_usb_scpi.py](owon_usb_scpi.py) is
  usable. It also have a debug CLI that allow for directly querying the device
  with proper data type interpretation.

  ```bash
  rlwrap ./owon_usb_scpi.py
  # Try the following commands:
  *IDN?

  # Show all voltage values
  values

  # Manually show channel data header
  json
  :data:wave:screen:head?

  # Manually dump CH1 value
  int
  :data:wave:screen:ch1?

  # Benchmark how fast you can read one channel screen data
  benchmark
  ```

  You can implemtn your own library on this using the SCPI commands documented in [HDS200_Series_SCPI_Protocol.md](HDS200_Series_SCPI_Protocol.md).
* A higher level interface for the HDS200 is in the works.

## Compatibility

I have only tested this with an OWON HDS272S, but I believe this is compatible
with all [HDS200 Series Oscilloscopes](https://www.owon.com.hk/products_owon_hds200_series_digital_oscilloscope) and probably all [HDS300 Series Oscilloscopes](https://www.owon.com.hk/products_owon_hds300_series_digital_oscilloscope).

It is also possible that this is compatible with the OWON PDS6062T Oscilloscope, since my HDS272S identifies itself with a USB vendor and product ID of the PDS6062T.
This could simply be due to OWON using the same vendor/product ID for all devices.

## Experiments

* Checkout the WebUSB demos/experiment [here](https://linux4life798.github.io/owon-hds200-capture/webusb/).
* Checkout the kernel module in [driver](driver) that allows you to interface with OWON devices via a serial interface. I am trying to upstream support for OWON devices into the existing usb-serial-simple driver via [this change](https://github.com/torvalds/linux/compare/master...linux4life798:linux-owon-hds200:owon-serial-simple-driver).
