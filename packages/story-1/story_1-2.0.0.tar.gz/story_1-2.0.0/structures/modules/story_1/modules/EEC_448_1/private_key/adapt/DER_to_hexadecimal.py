
#
#	https://stackoverflow.com/questions/6624453/whats-the-correct-way-to-convert-bytes-to-a-hex-string-in-python-3
#

import bytes

def start (
	DER_string
):
	hexadecimal_string = DER_string.hex ()
	assert (len (hexadecimal_string) == 146), len (hexadecimal_string)

	assert (
		bytes.fromhex (hexadecimal_string) == 
		DER_string
	)
	
	return hexadecimal_string;