

import hashlib as _hashlib
import string as _string

def Hash(text:str, hashFunc=_hashlib.sha1()) -> str:
    hashFunc.update(text.encode())
    return hashFunc.hexdigest()

def Random(length:int, charset=_string.ascii_letters + _string.digits):
    '''
    Generates random string with a specified length and consisting of specified charset
    
    :param charset: 
        * a simple string of different characters to sample the random string from.
            repeating same characters multiple times, increases probability of that character being picked more often.
        * You can enter your own characters or/and combine with defaults below.
            * string.ascii_lowercase - a-z
            * string.ascii_uppercase - A-Z
            * string.ascii_letters - lowercase + uppercase
            * string.digits - 0-9
            * string.punctuation -- all symbols
            * string.printable -- a string containing all ASCII characters considered printable
    '''
    import random

    return ''.join([random.choice(charset) for _ in range(length)])

def IndentText(text:str, indentLevel=0, indentStyle='\t'):
    ''' per indentLevel adds one indentStyle to each row '''
    
    if(indentLevel == 0):
        return text

    indentStyle = "".join([indentStyle]*indentLevel)
    return indentStyle + text.replace("\n", f"\n{indentStyle}")

def IsNullOrEmpty(text:str|None):
    if(text is None or text == ""):
        return True
    return False

def IsEqualIgnoreCase(text1:str, text2:str):
    return text1.lower() == text2.lower()

def IsEqualAnyIgnoreCase(searchText:str, textList:list[str]):
    lower_string = searchText.lower()
    for i in textList:
        if(lower_string == i.lower()):
            return True
    return False

def Sanitize(text:str, allowedCharset:str):
    return ''.join(c for c in text if c in allowedCharset)
