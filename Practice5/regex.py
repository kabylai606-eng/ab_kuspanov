#Match string: "a" followed by zero or more "b"
import re

pattern = r"ab*"

text = input("Enter string: ")

if re.fullmatch(pattern, text):
    print("Match")
else:
    print("No match")
    
    
#Match string:'a' followed by 2-3 'b'
import re

pattern = r"ab{2,3}"

text = input()

if re.fullmatch(pattern, text):
    print("Match")
else:
    print("No match")
    
    
#Find sequences of lowercase letters joined with underscore
import re

text = input()

pattern = r"[a-z]+_[a-z]+"

matches = re.findall(pattern, text)

print(matches)


#Uppercase letter followed by lowercase letter
import re

text = input()

pattern = r"[A-Z][a-z]+"

matches = re.findall(pattern, text)

print(matches)


#Match a...b
import re

text = input()

pattern = r"a.*b"

if re.fullmatch(pattern, text):
    print("Match")
else:
    print("No match")
    
    
#Replace space,comma,dot -> colon
import re

text = input()

result = re.sub(r"[ ,\.]", ":", text)

print(result)


#Snake case -> Camel case
import re

text = input()

result = re.sub(r"_([a-z])", lambda x: x.group(1).upper(), text)

print(result)


#Split string at uppercase letters
import re

text = input()

words = re.findall(r"[A-Z][^A-Z]*", text)

print(words)


#Insert spaces before capital letters
import re

text = input()

result = re.sub(r"([A-Z])", r" \1", text).strip()

print(result)


#Camelcase -> snake_case
import re

text = input()

result = re.sub(r"([A-Z])", r"_\1", text).lower().lstrip("_")

print(result)