from PIL import Image, ImageOps, ImageFilter, ImageEnhance

from effects import *
from tools import *
from recipes import Recipe, recipes_collection

def apply(img: Image, size = (1080, 1080), 
          recipe: Recipe = recipes_collection['CLSC']) -> Image:
    """Applies effect by given recipe
    """
    img = ImageOps.exif_transpose(img)
    # Crop
    img_contain = ImageOps.fit(img, size, centering=(0.55, 0.7))    

    # Color
    enhancer = ImageEnhance.Color(img_contain)
    img_contain = enhancer.enhance(1 + recipe.color)

    # Brightness
    br = ImageEnhance.Brightness(img_contain)
    img_contain = br.enhance(1 + recipe.brightness)
    
    # Contrast
    enh = ImageEnhance.Contrast(img_contain)
    img_contain = enh.enhance(1 + recipe.contrast)
    
    # Blur
    # The radius parameter in ImageFilter.GaussianBlur controls the strength 
    # of the blur. A smaller radius value results in a lighter blur, 
    # while a larger radius value increases the strength of the blur.
    img_contain = img_contain.filter(ImageFilter.GaussianBlur(recipe.blur)) 

    # Grain
    img_contain = grain(img_contain, recipe.grain)   

    # Sharpness
    sharper = ImageEnhance.Sharpness(img_contain)
    img_contain = sharper.enhance(1 + recipe.sharpness)    

    #  Tint
    img_contain = cbalance(img_contain, *recipe.tint)

    # Light leaks    
    img_contain = leaks(img_contain, **recipe.leaks)    
    
    # Vignette    
    img_contain = vignette(img_contain, **recipe.vignette) 

    # POST
    # post color
    enhancer = ImageEnhance.Color(img_contain)
    img_contain = enhancer.enhance(0.8)
        
    return img_contain

def open_apply_save(name, orig_path = "orig/", out_path = "out/", 
                    suffix="_edit", size = (1080, 1080), 
                    recipe: Recipe = recipes_collection['CLSC']) -> None:
    """Opens file, applies filter, saves the file
    name:
        filename to open
    orig_path:
        where to open
    out_path:
        where to save
    suffix:
        mark outputed filename
    """      
    orig = Image.open(orig_path+name)
    out = apply(orig, size=size, recipe=recipe)

    # save        
    o = out_path+suffixname(name, suffix)
    print("Saving: ", o)
    out.save(o)
    

