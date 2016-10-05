from glob import glob
from sys import argv
import os

directory = argv[1]
os.chdir(directory)
#        text = text.replace("vendor","vendors")
#        text = text.replace("Vendor","Vendors")
for py_file in glob("*"):
    with open(py_file,"r") as f:
        text = f.read()
    with open(py_file,"w") as f:
        text = text.replace("vendorssss","vendors")
        text = text.replace("vendorsss","vendors")
        text = text.replace("vendorss","vendors")
        text = text.replace("Vendorssss","Vendors")
        text = text.replace("Vendorsss","Vendors")
        text = text.replace("Vendorss","Vendors")
        f.write(text)
        

os.chdir("..")
