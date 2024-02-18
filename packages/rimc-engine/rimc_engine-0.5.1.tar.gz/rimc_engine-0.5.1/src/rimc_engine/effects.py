from PIL import Image, ImageFilter, ImageDraw
from PIL import ImageOps

import numpy as np
from random import randint


def vignette(image, sizep=0.1, transparency=0, brightness=150, density=60, frame="rect"):
    """
    Apply vignette 
    
    sizep: size of the vignette frame in percents of original image (0.-1.0)
    transparency: how transparent black mask is. (0-255) where 0 is fully dark
    brightness: brightness of the output print (0-255). More -> brighter
    density: overall visibility, controlled by blur (less - less visible)

    frame: geometrical types of vignette. Allowed values:
        "rect", "round"
    """
    # Open the image
    original_image = image
    width, height = original_image.size

    # get radius    
    radius = int(width/2*(1-1*sizep))

    # Create a mask 
    mask = Image.new('L', (width, height), transparency) 
    mask_draw = ImageDraw.Draw(mask)

    tc = brightness

    # Draw a figure on the mask
    _xy = (width // 2 - radius, height // 2 - radius,
           width // 2 + radius, height // 2 + radius)
    if frame == "rect":
        mask_draw.rounded_rectangle(_xy,
                                    fill=tc)
    elif frame == "round":
        mask_draw.ellipse(_xy,
                          fill=tc)
    else:
        raise ValueError("No such frame!")
    
    mask = mask.filter(ImageFilter.GaussianBlur(radius=radius/density))

    # Apply the mask to the image
    vignette_image = Image.new('RGB', (width, height))
    vignette_image.paste(original_image, (0, 0), mask)

    return vignette_image

def leaks(image, r_max=500, intensity=250, density=100, 
               offset=(0,0), transparency=200,
               uselines = False):
    """
    generate Light leaks / film burn and apply to the image
    
    r_max: max radius / measure of figures
    intensity: number of figures
    density: overall visibility of figures, controlled by blur
        Recommended values: from 50 to 100, with the lower value for the figures to be more blended
        after 100, figures are more recognisable
    offset: a border width (2-dimesional) to manipulate the concentration area of the figures
        e.g. (100, 50) will set the concentration area as: 
            100 < x < width-100, 50 < y < height-50
    transparency: maximum transparency (0-255)
    uselines: use lines in the artifact generation
    """
    # Open the image
    original_image = image
    width, height = original_image.size

    # convergent mask
    mask = Image.new('RGBA', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)

    
    for i in range(intensity):
        # draws: arcs, ellipses    
        # color layer
        # clayer = Image.new('RGB', (width, height), 0)    
        # clayer_draw = ImageDraw.Draw(clayer)
        
        # position
        x = randint(offset[0], width-offset[0])
        y = randint(offset[1], height-offset[1])

        # color
        # gradient - white / orange / red
        # 255, 255, 255
        # 229, 153, 23
        # 212, 13, 13
        r = randint(200, 255)
        if r == 255:
            gk = randint(69, 255) / 255
            if gk > 0.8:
                bk = gk
            else:
                bk = randint(0, 15) / 1000  

        elif r > 230:
            gk = randint(0, 110) / 100
            bk = randint(0, 20) / 100            
        else:
            gk = randint(0, 30) / 1000
            bk = randint(0, 30) / 1000            

        g = int(gk * r)
        b = int(bk * r)
        # color = (r, g, b)#(200, 0, 0)
        t = randint(100, transparency) # transparency
        tcolor = [r, g, b, t] 
        
        # measures
        r = (r_max//randint(1, 100),
             r_max//randint(1, 100),
             r_max//randint(1, 100),
             r_max//randint(1, 100),)
        
        _xy = (x - r[0], y - r[1]*randint(1,2),
               x + r[2], y + r[3]*randint(1,2))
        ang = [0, 0]
        if uselines:
            fig = randint(0, 9)
        else:
            fig = randint(0, 8)
        
        if 0 <= fig < 3:
            tcolor=tuple(tcolor)
            ang[0] = randint(0, 355)
            ang[1] = randint(0, 360 - ang[0]) + ang[0]
            mask_draw.arc(_xy,
                          start=ang[0], end=ang[1],
                          fill=tcolor,
                          width=5)
        elif 3 <= fig < 6:
            tcolor=tuple(tcolor)
            mask_draw.ellipse(_xy,                               
                              fill=tcolor)
        elif 6 <= fig < 8:
            tcolor=tuple(tcolor)
            ang[0] = randint(0, 355)
            ang[1] = randint(0, 360 - ang[0]) + ang[0]
            mask_draw.chord(_xy,
                          start=ang[0], end=ang[1],
                          fill=tcolor,
                          width=5)
        elif fig == 9:
            wp = 1+int(r_max/width*100) # max percentage of width
            w = int(width*randint(1, wp)/100/2)
            mt = 200 # max trans
            tcolor[3] = int(mt*(100-w/width)) # the less the width - more its intensity
            tcolor=tuple(tcolor)
            _xy = (x, 0, x, height)
            mask_draw.line(_xy,fill=tcolor, width=w)

        k = randint(2, 10)
        # mask = Image.blend(mask, clayer, 1/k)

    # smooth the effect
    mask = mask.filter(ImageFilter.GaussianBlur(radius=r_max/density))
    
    # Apply the mask to the image
    # mask = mask.convert("RGB") // loses alpha level
    mask_rgb = Image.new('RGB', (width, height), 0)
    mask_rgb.paste(mask, (0, 0), mask)

    img_spotted = Image.blend(original_image, mask_rgb, 0.1)    
    
    return img_spotted
    

def cbalance(image, rk = 0, gk = 0, bk = 0):
    """
    Add a color tint to the image.

    image: The input image.
    rk, gk, bk: Intensity of the reds, greens, and blues respectively
        (0.0 to 1.0)

    return: Image with added tint.
    """
    # Split the image into individual color channels
    r, g, b = image.split()

    # Adjust the red channel by adding a red tint
    r_tinted = r.point(lambda p: p + int(255 * rk))
    g_tinted = g.point(lambda p: p + int(255 * gk))
    b_tinted = b.point(lambda p: p + int(255 * bk))

    # Merge the modified red channel with the original green and blue channels
    tinted_image = Image.merge('RGB', (r_tinted, g_tinted, b_tinted))

    return tinted_image

def grain(image, intensity):
    """
    Add a grain effect to the image.

    image: The input image.
    intensity: Intensity of the grain effect (0.0 to 1.0). 
    0.2 is recommended maximum for artistic effect,
    0.1 is strong 
    0.05 for nice visible grain,
    
    return: Image with added grain effect.
    """
    # Convert the image to a NumPy array
    img_array = np.array(image)

    # Generate random Gaussian noise
    noise = np.random.normal(scale=intensity * 255, size=img_array.shape)

    # Add the noise to the image
    noisy_image_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)

    # Convert the NumPy array back to an image
    noisy_image = Image.fromarray(noisy_image_array)

    return noisy_image


def centered_crop(orig_img, size = 1080):    
    """Tooks orig_img and crops it into square of size [size x size]
    """
    img = ImageOps.exif_transpose(orig_img)
    aspect = orig_img.width / orig_img.height

    
    # Crop largest side, so the image become square
    if aspect > 1:
        # width > height
        crop_square = [orig_img.width / 2 - orig_img.height/2,
                       0,
                       orig_img.width / 2 + orig_img.height/2,
                       orig_img.height]
    elif aspect == 1:
        crop_square = None
    else:
        # width < height
        crop_square = [0,
                       orig_img.height/2 - orig_img.width / 2,
                       orig_img.width,
                       orig_img.height/2 + orig_img.width / 2]
    
    if crop_square != None:
        img = img.crop(crop_square)

    # resize it to fit requsted size    
    return img.resize((size,size), Image.LANCZOS)