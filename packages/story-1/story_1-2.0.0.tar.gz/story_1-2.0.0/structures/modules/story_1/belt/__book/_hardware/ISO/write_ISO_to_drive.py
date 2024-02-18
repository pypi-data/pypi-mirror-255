



#
#	⚠️
#		Make sure that "from_iso" is pointing to where you want it to be pointed.
#	

#
#	relevant:
#		https://askubuntu.com/questions/1333102/what-is-a-dd-command-to-write-the-ubuntu-iso-to-an-external-hard-drive-over-usb
#

from_iso = "ubuntu-22.04.1-desktop-amd64.iso"
to_drive = "/dev/sdc"

#
#	  bs = bytes        
#			read and write up to ____ bytes at a time (default: 512);
#			This overrides ibs and obs.
#
#			examples: 4M, 1M
#
# byte_size = "4096"
byte_size = "4M"


script = " ".join ([
	"sudo",
	"dd",
	f"if={ from_iso }",
	f"of={ to_drive }",
	f"bs={ byte_size }",
	"status=progress"
])

print (script);

#import os
#os.system (script)










#