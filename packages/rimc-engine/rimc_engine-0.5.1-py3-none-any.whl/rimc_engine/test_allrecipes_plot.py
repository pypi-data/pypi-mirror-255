from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import numpy as np

import os

from recipes import *
from convert_temp import apply
from tools import suffixname

out_path = '../../out/i/'
orig_path = '../../gallery/o/'
recipes = list(recipes_collection.keys())
print(recipes)
files = os.listdir(orig_path)
print(files)

def main():  
    def on_one_plot():
        if os.path.isfile(os.path.join(orig_path, f)):
            # for every photo apply all recipes

            original_image = Image.open(orig_path+f)
            img = ImageOps.exif_transpose(original_image)
            fig, axs = plt.subplots(4, 2, figsize=(7, 7))            
            
            axs[0, 0].imshow(np.asarray(img))
            axs[0, 0].axis('off')  # Turn off axis labels
            axs[0, 0].set_title("Original", fontsize=5)  # Add a title or label
            j = 0
            k = 1
            for i in range(len(recipes)):
                imgi = apply(img, recipe=recipes_collection[recipes[i]])
                
                if k == 2:
                    j += 1
                    k=0
                print(j, k)
                axs[j, k].imshow(np.asarray(imgi))
                axs[j, k].axis('off')  # Turn off axis labels
                axs[j, k].set_title(recipes[i], fontsize=5)  # Add a title or label
                k+=1

            plt.subplots_adjust(wspace=0, hspace=0.2)
            output_path = os.path.join(out_path,f)
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=300)
            # Show the figure
            # plt.show()
            
    def slit_by_two():
        if os.path.isfile(os.path.join(orig_path, f)):
            original_image = Image.open(orig_path+f)
            img = ImageOps.exif_transpose(original_image)
            
            k = 0
            j = 0
            
            for i in range(len(recipes)+1):
                k %= 2 
                if k%2 == 0:
                    fig, axs = plt.subplots(1, 2, figsize=(7, 7))
                       
                if j ==0 and k==0:
                    imgi = img
                else:
                    print(recipes[i-1])
                    imgi = apply(img, recipe=recipes_collection[recipes[i-1]])   
                
                axs[k].imshow(np.asarray(imgi))
                axs[k].axis('off') 

                k+=1
                if k%2 == 0:
                    j+=1
                    plt.subplots_adjust(wspace=0, hspace=0.2)
                    output_path = os.path.join(out_path,suffixname(f, str(j)))
                    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=300)

    

    f = "cows.JPG"
    slit_by_two()
         

if __name__ == "__main__":
    main()