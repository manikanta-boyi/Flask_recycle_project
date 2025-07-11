import os
from PIL import Image
from flask import current_app, url_for

def add_profile_pic(pic_upload,username):
    filename = pic_upload.Filename

    ext_type = filename.split('.')[-1]

    storage_filename = str(username)+'.'+ext_type

    filepath = os.path.join(current_app.root_path,'static\profile_pics',storage_filename)

    output_size = (200,200)

    pic = Image.open(pic_upload)

    pic.thumbnail(output_size)
    pic.save(filepath)

    return storage_filename