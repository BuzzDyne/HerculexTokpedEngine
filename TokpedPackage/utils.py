import base64

def encode(str):
    str_bytes = str.encode("ascii")

    base64_bytes = base64.b64encode(str_bytes)
    base64_string = base64_bytes.decode("ascii")

    return base64_string

def getItemFromListOfObject(listOfObjects, key, valueToMatch):
	for x in listOfObjects:
		if x[key] == valueToMatch:
			print("i found it!")
			break
	else:
		x = None