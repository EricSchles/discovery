import json
from sys import argv

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

with open(argv[1],"r") as f:
    dicter = json.loads(f.read())

for elem in dicter:
    for value in elem["fields"]:
        if type(value) == type(str()):
            if value.isdigit() or isfloat(value):
                print("found")
                
