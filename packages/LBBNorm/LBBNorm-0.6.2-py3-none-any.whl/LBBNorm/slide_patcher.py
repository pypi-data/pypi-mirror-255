
import numpy as np
from skimage import io
from skimage.color import rgb2hsv
from skimage.util import img_as_ubyte
from skimage import img_as_ubyte
from os import path, makedirs
from os.path import join 
import sys


openslide_error = False
try:
    import openslide as slide
except OSError as e:
    if "libopenslide.so.0" in str(e):
        openslide_error = True
    else:
        raise 


class WholeSlidePatcher():
    
    def __init__(self,patch_size=224 , step_size=10, folder='./patch_output',patched_folder='./patched',thumbnails_folder='./thumbnails'):
        if openslide_error:
            print("An error occurred due to missing 'libopenslide.so.0'.")
            print("Please ensure that libopenslide is installed on your system.")
            print("For Debian/Ubuntu: sudo apt-get install libopenslide0")
            print("For Fedora/Red Hat: sudo dnf install openslide")
            print("For macOS (using Homebrew): brew install openslide")
            print("Refer to the official OpenSlide documentation for more detailed installation instructions.")

        self.patch_size = patch_size
        self.step_size = step_size
        self.folder = folder
        self.patched_folder = patched_folder
        self.thumbnails_folder = thumbnails_folder
        
    def check_margins(self,img, t=15):
        img = rgb2hsv(img)
        h, w, c = img.shape
        sat_img = img[:, :, 1]
        sat_img = img_as_ubyte(sat_img)
        ave_sat = np.sum(sat_img) / (h * w)
        return ave_sat >= t

    def crop_slide(self,img, save_slide_path, position=(0, 0), step=(0, 0), patch_size=224): # position given as (x, y) 
            img = img.read_region((position[0] * 4, position[1] * 4), 1, (patch_size, patch_size))
            img = np.array(img)[..., :3]
            if self.check_margins(img, 30):
                patch_name = "{}_{}".format(step[0], step[1])
                io.imsave(join(save_slide_path, patch_name + ".jpg"), img_as_ubyte(img))       
                            
    def patch(self,slides):
        print('Initializing patching process...')
        if type(slides) == str:
            slides = [slides]
        makedirs(self.folder, exist_ok=True)
        out_base = self.folder+self.patched_folder
        makedirs(out_base, exist_ok=True)
        makedirs(self.folder+self.thumbnails_folder, exist_ok=True)
        
        for s in range(len(slides)):
            img_slide = slides[s]
            img_name = img_slide.split(path.sep)[-1].split('.')[0]
            bag_path = join(out_base, img_name)
            makedirs(bag_path, exist_ok=True)
            img = slide.OpenSlide(img_slide)
            dimension = img.level_dimensions[1] # given as width, height
            if self.folder=='test':
                thumbnail = np.array(img.get_thumbnail((int(dimension[0])/7, int(dimension[1])/7)))[..., :3]
            else:
                thumbnail = np.array(img.get_thumbnail((int(dimension[0])/28, int(dimension[1])/28)))[..., :3]
            #io.imsave(join(self.folder, 'thumbnails', img_name + ".png"), img_as_ubyte(thumbnail))        
            step_y_max = int(np.floor(dimension[1]/self.step_size)) # rows
            step_x_max = int(np.floor(dimension[0]/self.step_size)) # columns
            for j in range(step_y_max): # rows
                for i in range(step_x_max): # columns
                    self.crop_slide(img, bag_path, (i*self.step_size, j*self.step_size), step=(j, i), patch_size=self.patch_size)
                sys.stdout.write('\r Cropped: {}/{} -- {}/{}'.format(s+1, len(slides), j+1, step_y_max))
