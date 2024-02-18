class Units:   
    """Scaling parameters to map input of recipe to
    configurations of effects in effects.py
    """
    brightness = 0.1
    contrast = 0.1

    blur = 0.5
    sharpness = 0.15 

    color = 0.1
    cbalance = 0.01

    grain = 0.01 

class Presets:
    """Collection of configurations for filters. Supported effects:

    leaks : simulates light leaks as random soft artifacts,
    vignettes : makes vignette effect over the image,
    tints : color balance tint over the image.
    """
    # Light leaks
    leaks = {
        "clear":{"r_max":10, "intensity":1, 
                    "density":5, "transparency":250},
        "xlight":{"r_max":800, "intensity":10, 
                  "density":20, "offset":(0, 0),"transparency":240},
        "light":{"r_max":800, "intensity":50, 
                 "density":40, "offset":(50, 50),"transparency":250},
        "classic":{"r_max":1000, "intensity":200, 
                    "density":50, "offset":(100, 50),
                    "transparency":250, "uselines": False},        
        
        "rollers_light":{"r_max":700, "intensity":40, 
                         "density":20, "uselines": True}, 
        "rollers_medium":{"r_max":700, "intensity":100, 
                    "density":20, "uselines": True},
        "rollers_2":{"r_max":150, "intensity":500, 
                    "density":10, "uselines": True},
                   
        "linear1":{"r_max":150, "intensity":50, 
                    "density":60, "uselines": True},
        "linear2":{"r_max":100, "intensity":250, 
                    "density":40, "uselines": True}                 
    }
    vignettes = {
        "rect_clear":{"sizep":0.01, "transparency":100, 
                      "brightness":250, "density":60, "frame":'rect'},
        "rect_pale":{"sizep":0.01, "transparency":100, 
                     "brightness":220, "density":60, "frame":'rect'},
        "rect_strong":{"sizep":0.02, "transparency":0, 
                       "brightness":220, "density":60, "frame":'rect'},
        
        "round_xlight":{"sizep":0.05, "transparency":240,
                        "brightness":250, "density":5, "frame":"round"},
        "round_light":{"sizep":0.05, "transparency":220,
                       "brightness":200, "density":5, "frame":"round"},                
        "round":{"sizep":0.05, "transparency":120,
                 "brightness":250, "density":5, "frame":"round"}
    }
    tints = {
        "neutral":(0, 0, 0),
        "brown":(8, 0, -8),
        "red":(8, -4, -8),
        "blue":(-8, -4, 4),
        "portra":(3, 1, -5),
        "gold":(4, 0, -5),
        "superia":(4, 0.1, -3),
        "silvertone":(-1, -0.5, 1),
        "retro":(6, 3, -4),
        "polaroid600":(4, 0, 6),
    }

class Recipe:
    """Defines configuration set for filters
    """
    def __init__(self, name: str, altname: str,
                 brightness=0, contrast=0, blur=0,
                 sharpness=0, color=0, grain=0,
                 tint=Presets.tints["neutral"],
                 leaks=Presets.leaks["clear"],
                 vignette=Presets.vignettes["round_xlight"]
                 ):
        
        self.name = name
        self.altname = altname

        self.check(brightness, (-7, 7))
        self.brightness = brightness*Units.brightness

        self.check(contrast, (-4, 8))
        self.contrast = contrast*Units.contrast

        self.check(blur, (0, 5))
        self.blur = blur*Units.blur

        self.check(sharpness, (-5, 7))
        self.sharpness = sharpness*Units.sharpness
        
        self.check(color, (-10, 10))
        self.color = color*Units.color

        self.check(grain, (0, 10))
        self.grain = grain*Units.grain

        self.tint =  [c*Units.cbalance for c in tint]
        self.leaks = leaks
        self.vignette = vignette

    def check(self, value, x=(-5, 5)):
        if not (x[0] <= value <= x[1]):
            raise ValueError(f"This value ({value}) should be in range:", x)

""" Predefied collection of recipes """
recipes_collection = {
    'CLSC':Recipe(name='CLSC', altname="classic", 
                  brightness=2, contrast=4, blur=2,
                  sharpness=1, grain=2,
                  tint=Presets.tints["brown"],
                  leaks=Presets.leaks["classic"],
                  vignette=Presets.vignettes["rect_pale"]),
    'PORT':Recipe(name='PORT', altname="portra", 
                  brightness=1, contrast=-1, blur=0,
                  sharpness=-0.5, color=2.5, grain=2,
                  tint=Presets.tints["portra"],
                  vignette=Presets.vignettes["round_xlight"],
                  leaks=Presets.leaks["xlight"]),
    'GOLD':Recipe(name='GOLD', altname="gold", 
                  brightness=1, contrast=-0.5, blur=0,
                  sharpness=-1, color=3, grain=3,
                  tint=Presets.tints["gold"],
                  vignette=Presets.vignettes["round_xlight"],
                  leaks=Presets.leaks["xlight"]),
    'SUPR':Recipe(name='SUPR', altname="superia", 
                  brightness=0.5, contrast=0.7, blur=0.5,
                  sharpness=0, color=1, grain=4,
                  tint=Presets.tints["superia"],
                  vignette=Presets.vignettes["round_xlight"],
                  leaks=Presets.leaks["xlight"]),
    'bwSV':Recipe(name='bwSV', altname="bw silver", 
                  brightness=1.5, contrast=1.1, blur=0.5,
                  sharpness=1, color=-10, grain=2,
                  tint=Presets.tints["silvertone"],
                  vignette=Presets.vignettes["round_xlight"],
                  leaks=Presets.leaks["xlight"]),
    'bwRE':Recipe(name='bwRE', altname="bw retro", 
                  brightness=1, contrast=-0.5, blur=1,
                  sharpness=0, color=-10, grain=2,
                  tint=Presets.tints["retro"],
                  vignette=Presets.vignettes["round_xlight"],
                  leaks=Presets.leaks["xlight"]),
    'POL6':Recipe(name='POL6', altname="polaroid6xx", 
                  brightness=2, contrast=1, blur=1.5,
                  sharpness=-2, color=1, grain=4,
                  tint=Presets.tints["polaroid600"],
                  vignette=Presets.vignettes["round_light"],
                  leaks=Presets.leaks["rollers_light"]),
}
    

