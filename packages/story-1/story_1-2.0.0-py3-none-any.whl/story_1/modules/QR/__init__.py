w
'''
	qrcode
'''

'''
	<body>
		<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASIAAAEiAQAAAAB1xeIbAAABj0lEQVR4nO2ZS26EMBBEXwekLOEGcxRz5dwAHyU3sJcjMaosPJ5PoihZhIF42hIIwZNcQk253Jj4ecSXX0DglFNOOeXU3ik7jx7iCDblEMFaVNdTUEGSlICQQDOdJEn31ON1PQWVa42XugfKZ7C1rpap/vON8G6IvN6MTn1LxYNk0yNnfFqq1v0gIINBv4gMt5uuvapvgopmZjZS1lqbOJWYs7WupqlS99caVzws6L7q96v+f1OUKBm0lGRJkATDUh6UMe9VfRtU7iHoaJDNCKlT2WBNG+tqmTp7ThzBoFNx+GigeBC2la4nokIxnqPBIBFSVwxf87a6mqbOtj5zfdnV9C8n9/t1qHO+DzXa1FR56kUea9zZq/oWqGsfU/Ow3DR1NtbVNnXJmJKUumoyJWMuuOesSNWeQh4hvIHIIzAA1DVgv+rboszGTpB7zMaT5/tHUlI6GSEB5Fev+zWpz31M4lSaOj0MyXPOmhS3vwbpaisndbdNHV9rV6G+9DHLMSz1aiNdTjnllFNO/S31AYmly+gfYvsVAAAAAElFTkSuQmCC" />
	</body>
'''

import qrcode

def generate_QR_code (
	data = b""
):
	qr = qrcode.QRCode (
		version = 1,
		error_correction = qrcode.constants.ERROR_CORRECT_L,
		box_size = 10,
		border = 4
	)
	qr.add_data (data)
	qr.make (fit = True)

	img = qr.make_image (
		fill_color = "black", 
		back_color = "white"
	)
	
	bytes = BytesIO ()
	img.save (bytes)
	bytes.seek (0)
	
	base_64_image = b64encode (bytes.read ()).decode ()
	base_64_image_with_title = f'data:image/png;base64,{ base_64_image }';

	print (base_64_image)
