from __future__ import print_function
import colorsys
import numpy as np
try:
    from psp_tf.cityscapes_labels import trainId2label
    from psp_tf.ade20k_labels import ade20k_id2label
    from psp_tf.pascal_voc_labels import voc_id2label
except:
    from .psp_tf.cityscapes_labels import trainId2label
    from .psp_tf.ade20k_labels import ade20k_id2label
    from .psp_tf.pascal_voc_labels import voc_id2label

def class_image_to_image(class_id_image, class_id_to_rgb_map):
    """Map the class image to a rgb-color image."""
    colored_image = np.zeros((class_id_image.shape[0], class_id_image.shape[1], 3), np.uint8)
    for row in range(class_id_image.shape[0]):
        for col in range(class_id_image.shape[1]):
            try:
                colored_image[row, col, :] = class_id_to_rgb_map[int(class_id_image[row, col])].color
            except KeyError as key_error:
                print("Warning: could not resolve classid %s" % key_error)
    return colored_image


def color_class_image(class_image, model_name):
    """Color classed depending on the model used."""
    if 'cityscapes' in model_name:
        colored_image = class_image_to_image(class_image, trainId2label)
    elif 'voc' in model_name:
        colored_image = class_image_to_image(class_image, voc_id2label)
    elif 'ade20k' in model_name:
        colored_image = class_image_to_image(class_image, ade20k_id2label)
    else:
        colored_image = add_color(class_image)
    return colored_image


def color_class_image(class_image, model_name):
    """Color classed depending on the model used."""
    if 'cityscapes' in model_name:
        colored_image = class_image_to_image(class_image, trainId2label)
    elif 'voc' in model_name:
        colored_image = class_image_to_image(class_image, voc_id2label)
    elif 'ade20k' in model_name:
        colored_image = class_image_to_image(class_image, ade20k_id2label)
    else:
        colored_image = add_color(class_image)
    return colored_image


def add_color(img):
    """Color classes a good distance away from each other."""
    h, w = img.shape
    img_color = np.zeros((h, w, 3))
    for i in xrange(1, 151):
        img_color[img == i] = to_color(i)
    return img_color * 255  # is [0.0-1.0]  should be [0-255]


def to_color(category):
    """Map each category color a good distance away from each other on the HSV color space."""
    v = (category-1)*(137.5/360)
    return colorsys.hsv_to_rgb(v, 1, 1)
