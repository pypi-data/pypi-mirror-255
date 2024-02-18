# image to base64
from PIL import Image
import base64
import sys
import os
import imghdr
import shutil

# get PIL images by names
def get_images_by_names(path,names):
    
    img_list = []
    for name in names:
        try:
            img = Image.open(os.path.join(path, name))
            img_list.append(img)
        except FileNotFoundError:
            print("## Err: File not found - {}".format(name))
        except Exception as e:
            print("## Err: Failed to open image - {}: {}".format(name, str(e)))
    return img_list

# get images from folder
def get_img_from_folder(path, names):
    img_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(path, file)
            file_type = imghdr.what(file_path)
            if file_type in ["jpg", "jpeg", "png", "bmp", "webp"]:
                img = os.path.join(root, file)
                with open(img, 'rb') as f:
                    image_data = f.read()
                    base64_data = base64.b64encode(image_data,)
                    imgData = {
                        "data": base64_data.decode('utf-8'),
                        "name": file
                    }
                    img_list.append(imgData)
            else:
                os.remove(file)
                print("## Err: TYPE({})  {}".format(file_type, file)) 
    return img_list

# base64 to image
def base64_to_image(base64_data, dst_dir, name):
    imgdata = base64.b64decode(base64_data)
    file_path = os.path.join(dst_dir, name)
    file = open(file_path, 'wb')
    file.write(imgdata)
    file.close()
    file_type = imghdr.what(file_path)
    if file_type in ["jpg", "jpeg", "png", "bmp", "webp"]:
        new_file_name = "{}.{}".format(name, file_type)
        new_file_path = os.path.join(dst_dir, new_file_name)
        shutil.move(file_path, new_file_path)
        print("## OK:  {}  ".format(new_file_name))

# base64 list to image
def base64_list_to_image(base64_list, dst_dir, names):
    for index, img in enumerate(base64_list):
        base64_to_image(img, dst_dir, names[index])

# new image file
def new_image_file(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        for root, dirs, files in os.walk(path):
            for file in files:
                os.remove(os.path.join(root, file))
                
                
