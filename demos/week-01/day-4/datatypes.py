# Strings

# A string is just text - methods on strings return a new string. In that way they're 
# immutable like in many other languages

title = "  Login page returns 500  "
print(title)
print(title.strip())
print(title.strip().lower())
print(title.upper())
print(title) # The string is the same as when we started - these methods all return a new string
# and so far we haven't chosen to store it anywhere

title = title.strip()

print(title) # "Login page returns 500"

# Slicing strings
print(title[4])
print(title[:5]) # slice: first five characters 0-1-2-3-4
print(title[2:6]) # slice: chars between indexes 2 and 6 (not inclusive)
print(title[-3:]) # negative index - count back from the end then give me everything left

print(title.replace("500", "error")) # find and replace
 
# List of words (strings)
words = ["Login", "page", "returns", "500"]
 
# Basic string concat
sentence = words[0] + words[1] #and so on

# Joining strings with .join to avoid messy string concat code
new_sentence = " ".join(words)

# Another way to concat strings - format string or f-string
reporter = "Ada Lovelace"

formatted_report = f"{title} reported by {reporter}"

print(formatted_report)

# Casting
# Casting turns a value of one type into another type

# input always returns a string, we need to cast it before we can use it
ticket_id_from_user = input("What is the ticket id? ") # "42"

ticket_id = int(ticket_id_from_user) # 42

print(ticket_id, type(ticket_id_from_user), type(ticket_id))

# Converting a string to a floating point number
hours_open = float("5.5")

# This might not be needed in modern python, but I can convert other types 
# back into their string representations
print(str(101) + "tickets")

# 5.9 - casted to an int becomes just 5. Like in most other languages, python won't
# round when going from a float or decimal to an int. It just cuts off everything after
# the decimal point
hours_open = int(hours_open)


# print(int("3.0"))


# Booleans
# bool has two values - True and False. And like in JS, everything in Python
# is either "truthy" or "falsy"

is_open = True

# 0 is falsy
print(bool(0), bool(1), bool(-7))

# "" - empty string is falsy
print(bool(""), bool("hey"))

# Empty array is falsy
print(bool([]), bool([0, 1]))

print(bool("False")) # anything in a string satisfies "truthy-ness"

hours_left = 4 - hours_open # 4 - 5.5... so -1.5

# We can quickly assign a boolean by checking conditions
is_breached = is_open and hours_left < 0 

print(is_breached)

# and / or technically hand back one of the operands, not always True or False 
# you see this alot to assign default values quickly. In the case below, "" is falsy
# so python will default to assigning "unassigned"
assignee = "" or "unassigned"
print(assignee)
 
# Lists

# A list is an ordered, mutable collection. In python it is denoted by square brackets []
ticket_queue = ["Login page returns 500", "Password reset email missing", "Typo on footer"]
print(type(ticket_queue), len(ticket_queue))

# I can change the list in place 
ticket_queue.append("Search is slow") # adds this to the end of the list
ticket_queue.insert(0, "Site is down") # I can insert to a specific position

print(ticket_queue)

# Just like strings, we can slice and negative index, etc
print(ticket_queue[3])
print(ticket_queue[-1])
print(ticket_queue[1:3]) 

# When using lists for tracking things like orders or sequential records to be worked on
# or fed into some other system, etc. I can use things like pop()
print(ticket_queue)

removed = ticket_queue.pop() # removes the last item, and returns it so it can be stored, or otherwise 
# used in your code. 

print(removed)
print(ticket_queue)

# Sorting lists
# Depending on what you want to do with regards to the original list you have a few options for sorting
# a list in Python

# sorted() - this takes your list, and returns a NEW sorted copy. The original list is not touched
print(sorted(ticket_queue))
print(ticket_queue)

# sort() - if I want to sort the list in place, I call .sort(). It returns nothing and alters 
# your original list
print(ticket_queue.sort())
print(ticket_queue)

# Similar pitfalls/confusion can happen when trying to copy a list
ticket_queue_alias = ticket_queue # these refer to the same list in memory. I've created a pointer
ticket_queue_alias.append("Button misaligned")
print(ticket_queue) # accessing the list via the new reference... alters the underlying list. 
 
# If I want an actual copy that is distinct in memory, I need to use .copy()
ticket_queue_copy = ticket_queue.copy() # this returns a distinct copy of my list
ticket_queue_copy.append("Only in the copy")
print(ticket_queue)
print(ticket_queue_copy)

# Binary types
# So whenever we actually try to export anything (text, objects, etc) to save it to a disk
# or to send it over a network - we are serializing whatever that thing happens to be as Binary
# a literal stream of bytes. We can explore that more when we serialize data next week
# But we can play with the underlying byte type now

note = "café"
raw = note.encode("utf-8")

print(raw, type(raw))
print(len(note), len(raw)) # 4 chars, 5 bytes. é takes two bytes to represent 

print(raw.decode("utf-8")) # manually decoding our bytes back into a string

# bytearray
# here we're using a bytearray because bytes by themselves are immutable like strings 
# bytearray lets us treat it as separate bytes we can then work with it like a list of bytes
buffer = bytearray(raw) 
buffer.append(33) # Adding a new byte to my array, this will be whatever 33 happens to UTF-8 encode into
print(buffer.decode("utf-8"))

# NoneType - None means "no value here". In Python its it's own type with exactly one value "None"

assignee = None 
print(assignee, type(assignee))
print(assignee is None) # if we want to compare things that are/may be None, we use "is" not ==
print(assignee is not None) 


# Datetime - points in time, timestamps, lengths of times.
# comes up alot when working with data sets, as those are usually time stamped 

# I don't need to pip install any new packages, but I do need to ask for the code
from datetime import datetime, timedelta

# unlike basically everything else we've used so far, datetime is an object. Not a primitive built in type.
# we are calling a constructor here. And then satisfying the arguments of one of the datetime class's 
# many constructors
opened = datetime(2026, 10, 15, 11, 17) # year, month, day, hour (24z), minute

# When we call print() and pass it our opened datetime object, we are calling it's "__str__()"
# method. 
print(opened, type(opened))

# SLA - service level agreement (not a python thing, just for demo)
sla = timedelta(hours=4)
due = opened + sla # adding our time delta of 4 hours to the opened datetime
print(due) 

# Give me the time right now - based on your system time. 
now = datetime.now()

age = now - opened # datetime minus a datetime gives a timedelta
print(age, type(age))

print(age.total_seconds())

# By default datetimes get printed as ISO format
# I can also set my own format
print(opened.isoformat())

print(opened.strftime("%Y-%m-%d %H")) # creating a custom datetime output format (string)

# We can go the other way - parse a string into a date time according to this format
parsed_date = datetime.strptime("2026-10-15 14:00", "%Y-%m-%d %H:%M")
print(parsed_date)
# print(dir(__builtins__))