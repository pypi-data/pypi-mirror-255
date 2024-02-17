import string as _string

class Charsets:
    LowerCase = _string.ascii_lowercase
    '''includes: a-z'''
    UpperCase = _string.ascii_uppercase
    '''includes: A-Z'''
    Numbers = _string.digits
    '''includes: 0-9'''
    Letters = _string.ascii_letters
    '''includes: a-z A-Z'''
    LettersAndNumbers = Numbers + Letters
    '''includes: a-z A-Z 0-9'''
    Hex = _string.hexdigits
    '''includes: a-f A-F 0-9'''
    Symbols = _string.punctuation
    '''includes: all symbols such as !?@...'''
    Whitespace = _string.whitespace
    '''includes: all type of whitespaces even tabs, newlines etc'''
    Printables = _string.printable
    '''includes: all characters that are printable and not binary'''

class PermutationGenerator:
    def __init__(self, patternList: list[str]) -> None:
        self._patternList = patternList

    def __IncrementPatternIndexes(self):
        i = len(self._patternStates) - 1
        for patternState in reversed(self._patternStates):
            patternIndex, pattern = patternState
            if(i == 0): #first position in generatedString
                if(patternIndex == len(pattern)-1):
                    return False

            if(patternIndex < len(pattern) - 1):
                patternState[0] += 1
                self._buffer[i] = pattern[patternState[0]]
                return True
            else:
                patternState[0] = 0
                self._buffer[i] = pattern[0]
            i -= 1            
        return False

    def __GenerateString(self):
        generatedString = "".join(self._buffer)
        didIncrement = self.__IncrementPatternIndexes()
        if not didIncrement:
            self._flag_exhausted = True
        return generatedString
    
    def __iter__(self):
        self._patternStates: list[list] = []
        self._buffer = []
        self._flag_exhausted = False
        for charset in self._patternList:
            self._patternStates.append([0, charset])
            self._buffer.append(charset[0])
        return self

    def __next__(self):
        if(self._flag_exhausted):
            raise StopIteration
        return self.__GenerateString()