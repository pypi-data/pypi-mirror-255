

'''
	{ verify, approve, validate, certify, vouch }
'''

'''
	import story_1.modules.EEC_448_1.verify as verify
	verified = verify.start (
		public_key_string,
		
		signed_bytes = signed_bytes,
		unsigned_bytes = unsigned_bytes
	)
'''

from Crypto.Signature import eddsa
from Crypto.PublicKey import ECC

from story_1.modules.EEC_448_1.public_key.scan import scan_public_key

def start (
	#public_key_string = None,
	public_key_path = None,
	
	unsigned_bytes = None,
	signed_bytes = None
):
	[ public_key_instance, public_key_bytes, public_key_string ] = scan_public_key (public_key_path)

	#public_key_instance = ECC.import_key (public_key_string)
	verifier = eddsa.new (public_key_instance, 'rfc8032')
	
	try:
		verifier.verify (unsigned_bytes, signed_bytes)		
		return True;
		
	except Exceptions as E:
		pass;
				
	return False;