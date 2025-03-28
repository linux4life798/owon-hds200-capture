# This can be built without checking out the linux source tree.
# You just need to install the following Debian packages:
#
# apt install build-essential linux-headers-amd64

obj-m := owon.o

KERNELDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all: checkdep
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean

insmod: all
	sudo insmod owon.ko

rmmod:
	sudo rmmod owon

install: all
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules_install
	depmod -a

uninstall:
	rm -f /lib/modules/$(shell uname -r)/extra/owon.ko
	depmod -a

checkdep:
	@if [ ! -d $(KERNELDIR) ]; then \
		echo "Kernel directory $(KERNELDIR) does not exist"; \
		echo "sudo apt install linux-headers-amd64 build-essential"; \
		exit 1; \
	fi
