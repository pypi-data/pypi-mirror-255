





def smoothly (
	path = "", 
	private_key_string  = "", 
	format  = ""
):
	if (os.path.exists (path)):
		raise Exception (f"The path for the private_key is not available. '{ path }'");
	
	if (format == "DER"):
		f = open (path, 'wb')
	elif (format == "PEM"):
		f = open (path, 'w')
	else:
		raise Exception (f"format '{ format }' was not accounted for.")
	
	f.write (private_key_string)
	f.close ()
	
	return True
