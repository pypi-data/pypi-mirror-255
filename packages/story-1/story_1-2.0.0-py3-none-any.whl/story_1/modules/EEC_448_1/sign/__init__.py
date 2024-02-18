

'''
	import story_1.modules.EEC_448_1.sign as sign
	signed = sign.start (
		private_key_string,
		unsigned_bytes = unsigned_bytes
	)
	
	signed_bytes = signed.bytes
'''

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

import story_1.modules.EEC_448_1.private_key.scan as private_scan

def WRITE (PATH, SIGNED_MESSAGE):
	import os.path
	if (os.path.exists (PATH)):
		print ("PATH FOR SIGNED MESSAGE ISN'T EMPTY, EXITING.");
		exit ()
		return False;
	
	f = open (PATH, 'wb')
	f.write (SIGNED_MESSAGE)
	f.close ()


def start (
	private_key_path = None,
	unsigned_bytes = None
):
	private_key = private_scan.start (private_key_path)

	signer = eddsa.new (private_key.instance, 'rfc8032')
	signed_bytes = signer.sign (unsigned_bytes)
	
	#if (len (PATH) >= 1):
	#	WRITE (PATH, SIGNED_MESSAGE)
	
	class signed:
		def __init__ (this, signed_bytes):
			this.bytes = signed_bytes
		
	return signed (
		signed_bytes
	)
	
