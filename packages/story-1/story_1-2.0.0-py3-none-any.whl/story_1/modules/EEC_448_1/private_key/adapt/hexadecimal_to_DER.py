

import bytes

def start (
	hexadecimal_string
):
	DER_string = bytes.fromhex (hexadecimal_string)
	
	assert (len (DER_string.hex ()) == 146), len (hexadecimal_string)

	assert (
		hexadecimal_string == 
		DER_string.hex ()
	)
	
	return DER_string
