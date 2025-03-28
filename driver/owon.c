// SPDX-License-Identifier: GPL-2.0
/*
 * USB OWON Oscilloscope driver
 *
 * Copyright (C) 2025 Craig Hesling <craig@hesling.com>
 *
 * An in-tree version of this driver can be found here:
 * https://github.com/linux4life798/linux-owon-hds200
 */

#include <linux/kernel.h>
#include <linux/tty.h>
#include <linux/module.h>
#include <linux/usb.h>
#include <linux/usb/serial.h>

static const struct usb_device_id owon_id_table[] = {
	{ USB_DEVICE(0x5345, 0x1234) } /* Owon HDS200 Series Oscilloscopes */,
	{ },
};
MODULE_DEVICE_TABLE(usb, owon_id_table);

static struct usb_serial_driver owon_device = {
	.driver = {
		.owner =	THIS_MODULE,
		.name =		"owon",
	},
	.id_table =		owon_id_table,
	.num_ports =		1,
};

static struct usb_serial_driver * const serial_drivers[] = {
	&owon_device,
	NULL
};

module_usb_serial_driver(serial_drivers, owon_id_table);

MODULE_AUTHOR("Craig Hesling <craig@hesling.com>");
MODULE_DESCRIPTION("USB OWON Oscilloscope Serial Driver");
MODULE_LICENSE("GPL v2");
