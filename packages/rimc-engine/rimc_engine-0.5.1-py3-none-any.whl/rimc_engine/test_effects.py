from PIL import Image, ImageFilter, ImageOps, ImageEnhance

from effects import *
from tools import *

from recipes import Units, Presets

image_path = 'bike.jpg'
out_path = '../../out/'
orig_path = '../../orig/'

original_image = Image.open(orig_path+image_path)
img = ImageOps.exif_transpose(original_image)

# original_image.show()
# Apply Gaussian blur with different radii
for k in Presets.tints.keys():
    # enhancer = ImageEnhance.Contrast(original_image)
    # resulted_img = enhancer.enhance(1 + k*Units.contrast)

    # resulted_img = grain(original_image, k/100) 
    k = (c*Units.cbalance for c in Presets.tints[k])
    resulted_img = cbalance(original_image, *k)    

    # resulted_img = original_image.filter(ImageFilter.GaussianBlur(radius=radius))
    # print(k/100)
    
    resulted_img.show(title=str(k))
