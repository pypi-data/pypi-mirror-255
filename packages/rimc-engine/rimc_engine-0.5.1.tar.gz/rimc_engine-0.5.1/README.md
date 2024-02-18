# RIMC (Retro Image Converter) Engine for Python

Film simulation python module.
It allows you to convert any photo of your choice to the filtered image in a preferred vintage style!

## Features

- applying OOTB filters right after pip install
- easy to create filters with configuration presets
- bunch of effects you can combine in our own way

### Out of the box filters
- **Classic** `['CLSC']` : this configuration simulates overall look and feel of vintage photography. It was the first filter implemented in the RIMC.
- **Gold** `['GOLD']` : simulates Gold with it's warm tones
- **Portra** `['PORT']` : balanced tones with a little greenish pop
- **Superia** `['SUPR']` : crisp sharp looks with fine grain and natural colors
- **Polaroid 6xx** `['POL6']` : enhanced red and blue tones, along with reduced sharpness and intentionally introduced artifacts, collectively produce an output reminiscent of a photograph captured on authentic instant film with a plastic lens camera
- **Black&White Retro** `['bwRE']` : natural soft black and white of old age 
- **Black&White Silver** `['bwSV']` : high contrast modern black and white

You can create your own filter (see [Recipes](#recipes))

## Examples of output

<table>
  <tr>
    <th>Original</th>
    <th>Classic</th>
  </tr>
  <tr>
    <td><img src="gallery/cows/cowscrop.JPG" width="500"></td>
    <td><img src="gallery/cows/cowsCLSC.JPG" width="500"></td>
  </tr>
  <tr>
    <th>Gold</th>
    <th>Portra</th>
  </tr>
  <tr>
    <td><img src="gallery/cows/cowsGOLD.JPG" width="500"></td>
    <td><img src="gallery/cows/cowsPORT.JPG" width="500"></td>
  </tr>
  <tr>
    <th>Superia</th>
    <th>Polaroid 6xx</th>
  </tr>
  <tr>
    <td><img src="gallery/cows/cowsSUPR.JPG" width="500"></td>
    <td><img src="gallery/cows/cowsPOL6.JPG" width="500"></td>
  </tr>
  <tr>
    <th>BW Retro</th>
    <th>BW Silver</th>
  </tr>
  <tr>
    <td><img src="gallery/cows/cowsbwRE.JPG" width="500"></td>
    <td><img src="gallery/cows/cowsbwSV.JPG" width="500"></td>
  </tr>
</table>

Please visit [gallery](/gallery) for more examples.

## Usage

### Installation

Prerequisites
```bash
pip install pillow
pip install numpy
```
Install rimc engine
```bash
pip install rimc-engine
```
Update rimc engine
```bash
pip install --upgrade rimc-engine
```

### How to apply filter
You can just open python in a terminal and specify filename for which filter should be applied, and the recipe you want to be applied.
```python
name = "bike.jpg" # my image name
orig_path = "" # where this image is, use empty if it is in current folder
out_path = "" # where you want to store output image
```
Don't worry about name conflicts, the apply and save function will add "_edit" on the output file's name (so input image and output image can exist in one folder).

Next is choosing recipe (optional). If you will not specify it, the function will choose CLASSIC by default. For one of the OOTB filters, use `recipes_collection` dictionary (for key reference visit [OOTB Filters](#out-of-the-box-filters)). In this example we will use `'POL6'`:
```python
import rimc_engine as rimc
recipe = rimc.recipes_collection['POL6']
rimc.open_apply_save(name=name,orig_path=orig_path,out_path=out_path,recipe=recipe)
```
So that's how it's done, now you have `bike_edit.jpg` in your folder with applied filter!

There is more comprehensive example in `/tests/main.py`.

### Recipes

A **recipe** is a configuration set for series of filters to be applied to the original image. This module has a predefined collection (dictionary) of recipes named `recipes_collection`.

#### Creating a recipe
Recipe is a class, which just defines parameters for filters.

Number values (float values also accepted):
- brightness - with this you can increase or decrease brightness. E.g. -7 will give a very darken image, and +7 very bright.
- contrast - same as brightness, it controls contrast. Values: (-4, 8)
- blur - adds gaussian blur, which drastically softens an image. Values (0, 5)
- sharpness - more finer adjustment then blur, plus it allows to increase sharpness. (-5, 7)
- color - controls color saturation of the image. Values (-10, 10), where -10 will result in Monochrome
- grain - adds grain. Values (0, 10), where 5 is already a really strong visible grain, 10 will result as a noisy high-ISO film print.

Tuples:
- tint : (red, green, blue) - controls color balance. E.g. (5,0,5) will result in noticeable increase of reds and blues in the image. You can provide your own tuple, or use the one from `Presets.tints`.

Dictionaries:
- leaks - controls artifacts created on the image to simulate light leaks. They can be described as soft colored spots caused by direct influence of light on the film. It is recommended to just choose one from [Presets.leaks](#leaks).
- vignette - controls shadowing on the top-level mask of the image. It can manifest as a rounded gradient of shade, resembling the classic vignette, or as a more recognizable shadow that gradually fades, creating a vintage appearance in the photo. It is recommended to just choose one from [Presets.vignettes](#vignettes).

###### Study case
Let's take a look on the example from one of predefined recipes:
```python
Recipe(name='PORT', 
       brightness=1, contrast=-1, blur=0,
       sharpness=-0.5, color=2.5, grain=2,
       tint=Presets.tints["portra"],
       vignette=Presets.vignettes["round_xlight"],
       leaks=Presets.leaks["xlight"]),
```
How this configuration will affect the image:
- `brightness=1`: will slightly increase brightness,
- `contrast=-1, blur=0, sharpness=-0.5`: by decreasing contrast and sharpness it makes the picture to look softer, but sharpness is only slighly decreased and no blur applied, which will keep it sharp overall,
- `color=2.5`: boost colors, but they will still look about natural
- `grain=2`: is a setting for fine grain of lower ISO
- `tint=Presets.tints["portra"]`: will apply [R:+3, G:+1, B:-5] color balance, which gives enough space for reds, slighly enhances greens to match the tone of original portra film, and reduces blues to impart a warm tone to the image.
- `vignette=Presets.vignettes["round_xlight"]`: **round_xlight** is a type of vignette in rimc, which keeps image bright and gives pale round shade
- `leaks=Presets.leaks["xlight"]`: will simulate very rare weak light leaks artifacts on the picture.

This recipe transforms the original image into a fine-grain picture, featuring accurate yet more appealing colors, along with a neutral contrast that achieves a pleasing aesthetic.

### Presets reference

Presets contains configurations for artistic effects you can use for your recipes.

#### Leaks
Type 1 - random shapes and appearance (aka light leaks)
- ["clear"] : almost doesn't affect the picture
- ["xlight"] : very rare weak light leaks artifacts
- ["light"] : more frequent and strong light leaks artifacts
- ["classic"] : recognizable dense effect of light leaks

Type 2 - traces which instant-camera rollers leave
- ["rollers_light"] : weak effect of roller traces
- ["rollers_medium"] : increased intensity
- ["rollers_2"] : smaller traces with less density, but more frequent

Type 3 - scanlines
- ["linear1"] : recognizible color lines
- ["linear2"] : more intense, but smaller

#### Vignettes
Type 1 - rectangle, by-side shadowing
- ["rect_clear"] : almost not recognizable
- ["rect_pale"] : small shadow, which slightly reduces brightness
- ["rect_strong"] : recognizable aged-look shadowing

Type 2 - round, classic vignette
- ["round_xlight"] : almost not recognizable
- ["round_light"] : reduces brightness, but it's shape is still not really noticable
- ["round"] : recognizable shape with almost no decrease in brightness

#### Tints
- "neutral":(0, 0, 0),
- "brown":(8, 0, -8),
- "red":(8, -4, -8),
- "blue":(-8, -4, 4),
- "portra":(3, 1, -5),
- "gold":(4, 0, -5),
- "superia":(4, 0.1, -3),
- "silvertone":(-1, -0.5, 1),
- "retro":(6, 3, -4),
- "polaroid600":(4, 0, 6)




