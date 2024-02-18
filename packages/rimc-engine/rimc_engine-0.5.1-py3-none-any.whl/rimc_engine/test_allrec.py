from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import numpy as np

import os

from recipes import *
from convert_temp import open_apply_save
from effects import centered_crop
from tools import suffixname

out_path = '../../out/i/'
orig_path = '../../orig/o/'
recipes = list(recipes_collection.keys())
files = os.listdir(orig_path)
print(recipes)
print(files)

def process_one(f):
        for i in range(len(recipes)):
            open_apply_save(f, suffix=str(recipes[i]), recipe=recipes_collection[recipes[i]],
                            orig_path=orig_path, out_path=out_path)
            
def savecrop(f):
    orig = Image.open(orig_path+f)
    orig = ImageOps.exif_transpose(orig)

    out = centered_crop(orig)

    o = out_path+suffixname(f, "crop")
    print("Saving crop: ", o)
    out.save(o)


def main(): 
    test_collection = False
    if test_collection:
        # test recipe collection for image         
        f = files[1]
        process_one(f)

    
    makecrops = True
    if makecrops:
        for f in files:
            if os.path.isfile(os.path.join(orig_path, f)):
                savecrop(f)
        

if __name__ == "__main__":
    main()
