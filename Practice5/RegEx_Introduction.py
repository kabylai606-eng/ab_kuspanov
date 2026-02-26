#Python has a built-in package called re, which can be used to work with Regular Expressions.
#Import the re module:

import re

#Search the string to see if it starts with "The" and ends with "Spain":

import re

txt = "The rain in Spain"
x = re.search("^The.*Spain$", txt)