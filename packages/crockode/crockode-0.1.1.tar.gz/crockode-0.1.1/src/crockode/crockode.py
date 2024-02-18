""" Encode and Decode functions to convert strings between text and DNA base seqeunces 
"""

from .utils import convert_to_binary, convert_to_string

mapping = {
    "00": "A",
    "01": "G",
    "10": "C",
    "11": "T"
}

DNA_to_bin = {
    "A": "00",
    "G": "01",
    "C": "10",
    "T": "11"
}


def encode_string(text_inp: str) -> str:
    """ Encode a text string into DNA base sequence (ATCG)"

    Args:
        input (str): input text

    Returns:
        str: Encoded DNA sequence
    """
    binary_seq = convert_to_binary(text_inp)
    bin_lst = [binary_seq[i: i+2] for i in range(0, len(binary_seq), 2)]
    dna_lst = []
    for num in bin_lst:
        for key in list(mapping.keys()):
            if num == key:
                dna_lst.append(mapping.get(key))

    dna_seq = "".join(dna_lst)
    return dna_seq


def decode_dna(dna_inp: str) -> str:
    """Take in a DNA sequence and decode to text string

    Args:
        DNA_inp (str): DNA sequence 

    Returns:
        str: text string
    """
    bin_lst = []
    for base in dna_inp:
        for key in list(DNA_to_bin):
            if base == key:
                bin_lst.append(DNA_to_bin.get(key))
    bin_seq = "".join(bin_lst)
    return convert_to_string(bin_seq)
