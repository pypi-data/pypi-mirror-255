""" Util functions to convert sequences between text and binary.
"""

def convert_to_binary(text_inp: str)-> str:
    """ Convert text string input to a binary string sequence 

	Args:
		text_inp (str): text string

	Returns:
		str: Binary sequence
	"""
    return ''.join(format(x, '08b') for x in bytearray(text_inp, 'utf-8'))

def convert_to_string(binary_string: str) -> str:
    """ Convert binary string seqeunce to text string

    Args:
        binary_string (str): Binary sequence

    Returns:
        str: text string
    """
    # Split the binary string into 8-bit chunks
    chunks = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    # Convert each 8-bit chunk to an integer and then to a character
    characters = [chr(int(chunk, 2)) for chunk in chunks]
    # Join the characters to form the original string
    return ''.join(characters)
