from io import BytesIO

def suffixname(name, suffix):
    n = name.split('.')    
    return n[0]+suffix+'.'+n[1]

def buffer2upload(var_img, name, DjangoInMemoryUploadedFile, suffix="crop"):
    # Save the image in memory
    var_img_buffer = BytesIO()
    var_img.save(var_img_buffer, format='JPEG')
    
    memory_img = DjangoInMemoryUploadedFile(
        var_img_buffer,
        None,
        suffixname(name, suffix),
        'image/jpeg',
        var_img_buffer.tell(),
        None
    )
    return memory_img