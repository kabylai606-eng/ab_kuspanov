#Flags
#You can add flags to the pattern when using regular expressions.

# re.ASCII - re.A - Returns only ASCII matches
import re

txt = "Åland"

#Find all ASCII matches:
print(re.findall("\w", txt, re.ASCII))

#Without the flag, the example would return all character:
print(re.findall("\w", txt))


#Same result using the shorthand re.A flag:
print(re.findall("\w", txt, re.A))


# re.DEBUG - Returns debug information
import re

txt = "The rain in Spain"

#Use a case-insensitive search when finding a match for Spain in the text:

print(re.findall("spain", txt, re.DEBUG))


# re.DOTALL - re.S - Makes the . character match all characters (including newline character)
import re

txt = """Hi
my
name
is
Sally"""

#Search for a sequence that starts with "me", followed by one character, even a newline character, and continues with "is":
print(re.findall("me.is", txt, re.DOTALL))

#This example would return no match without the re.DOTALL flag:
print(re.findall("me.is", txt))


#Same result with the shorthand re.S flag:
print(re.findall("me.is", txt, re.S))


# re.IGNORECASE - re.I - Case-insensitive matching
import re

txt = "The rain in Spain"

#Use a case-insensitive search when finding a match for Spain in the text:
print(re.findall("spain", txt, re.IGNORECASE))


#Same result using the shorthand re.I flag:
print(re.findall("spain", txt, re.I))


# re.MULTILINE - re.M - Returns only matches at the beginning of each line
import re

txt = """There
aint much
rain in 
Spain"""

#Search for the sequence "ain", at the beginning of a line:
print(re.findall("^ain", txt, re.MULTILINE))

#This example would return no matches without the re.MULTILINE flag, because the ^ character without re.MULTILINE only get a match at the very beginning of the text:
print(re.findall("^ain", txt))


#Same result with the shorthand re.M flag:
print(re.findall("^ain", txt, re.M))


# re.UNICODE - re.U - Returns Unicode matches. This is default from Python 3. For Python 2: use this flag to return only Unicode matches
import re

txt = "Åland"

#Find all UNICODE matches:
print(re.findall("\w", txt, re.UNICODE))


#Same result using the shorthand re.U flag:
print(re.findall("\w", txt, re.U))


# re.VERBOSE - re.X - Allows whitespaces and comments inside patterns. Makes the pattern more readable
import re

text = "The rain in Spain falls mainly on the plain"

#Find and return words that contains the phrase "ain":

pattern = """
[A-Za-z]* #starts with any letter
ain+      #contains 'ain'
[a-z]*    #followed by any small letter
"""

print(re.findall(pattern, text, re.VERBOSE))

#The example would return nothing without the re.VERBOSE flag
print(re.findall(pattern, text))


#Same result with the shorthand re.X flag:
print(re.findall(pattern, text, re.X))