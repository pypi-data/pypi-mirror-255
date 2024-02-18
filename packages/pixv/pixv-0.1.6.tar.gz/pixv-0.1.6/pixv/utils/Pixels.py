from PIL import Image
import numpy as np

def image_to_array(image_path):
    # Open the image using Pillow
    image = Image.open(image_path)

    # Convert the image to a NumPy array
    image_array = np.array(image)
    image_array = image_array.astype(np.int64)

    return image_array



def is_image_changed(image1,image2):
    
    return not np.array_equal(image1, image2)

def modify_image(image_path:str,image:np.ndarray):
    try:
        img = Image.fromarray(image)
        img.save(image_path)
        return True
    
    except Exception as e:
        print(f"An error occured :{e}")
        return False

