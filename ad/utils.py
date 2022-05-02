import json
import cv2
import os
from scipy.interpolate import UnivariateSpline
import numpy as np
from ad.path import *


def read_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def write_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)


def bgr_to_rgb(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def adjust_saturation(img, degree=1.4):
    imghsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype('float32')
    h, s, v = cv2.split(imghsv)
    s = degree * s
    s = np.clip(s, 0, 255)
    imghsv = cv2.merge([h, s, v])
    saturated = cv2.cvtColor(imghsv.astype('uint8'), cv2.COLOR_HSV2BGR)
    return saturated


def adjust_contrast_brightness(image, alpha=2.5, beta=1.5):
    '''
        alpha: parameter for contrast
        beta: parameter for brightness
    '''
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted


def increase_sharpness(image):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    image_sharp = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    return image_sharp


def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized


def merge_image(back, front, x_offset,y_offset):
    y1, y2 = y_offset, y_offset + front.shape[0]
    x1, x2 = x_offset, x_offset + front.shape[1]

    alpha_s = front[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        back[y1:y2, x1:x2, c] = (alpha_s * front[:, :, c] +
                                  alpha_l * back[y1:y2, x1:x2, c])

    return back


class ProcessImage:
    def enhanceImage(self, image, alpha=1.15, beta=1.5, saturation=1.15):
        image = adjust_saturation(image, degree=saturation)
        image = adjust_contrast_brightness(image, alpha, beta)
        image = increase_sharpness(image)
        return image

    def darkFilter(self, image):
        decrease_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 25, 75, 255])(range(256))

        blue_channel, green_channel, red_channel = cv2.split(image)

        # decrease red channel
        red_channel = cv2.LUT(red_channel, decrease_table).astype('uint8')

        # decrease blue channel
        blue_channel = cv2.LUT(blue_channel, decrease_table).astype('uint8')

        # decrease green channel
        green_channel = cv2.LUT(green_channel, decrease_table).astype('uint8')

        output_image = cv2.merge([blue_channel, green_channel, red_channel])

        return output_image

    def warmFilter(self, image):
        increase_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 85, 165, 255])(range(256))
        decrease_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 35, 85, 255])(range(256))

        blue_channel, green_channel, red_channel = cv2.split(image)

        # increase red channel
        red_channel = cv2.LUT(red_channel, increase_table).astype('uint8')

        # decrease blue channel
        blue_channel = cv2.LUT(blue_channel, decrease_table).astype('uint8')

        output_image = cv2.merge([blue_channel, green_channel, red_channel])

        return output_image

    def coldFilter(self, image):
        increase_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 85, 165, 255])(range(256))
        decrease_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 35, 85, 255])(range(256))

        blue_channel, green_channel, red_channel = cv2.split(image)

        # decrease red channel
        red_channel = cv2.LUT(red_channel, decrease_table).astype('uint8')

        # increase blue channel
        blue_channel = cv2.LUT(blue_channel, increase_table).astype('uint8')

        output_image = cv2.merge([blue_channel, green_channel, red_channel])

        return output_image


def generate_output_image(path_background, path_logo, path_cta, path_shoe, enhancement_type, filter_type, message):
    process_image = ProcessImage()
    bg = cv2.imread(os.path.join(STATIC_DIR, path_background))
    if filter_type != 'None':
        bg = getattr(process_image, filter_type)(bg)

    if enhancement_type != 'None':
        bg = getattr(process_image, enhancement_type)(bg)

    ## add logo
    front_logo = cv2.imread(os.path.join(STATIC_DIR, path_logo), -1)
    front_logo = image_resize(front_logo, height=176)
    merged = merge_image(bg, front_logo, 820, 150)

    ## add shoe
    front_prod = cv2.imread(os.path.join(STATIC_DIR, path_shoe), -1)
    front_prod = image_resize(front_prod, height=600)
    merged = merge_image(merged, front_prod, 100, 150)

    ## add cta
    front_cta = cv2.imread(os.path.join(STATIC_DIR, path_cta), -1)
    front_cta = image_resize(front_cta, width=300)
    merged = merge_image(merged, front_cta, 750, 350)

    ## add text
    ad_texts_in_store = read_json(AD_TEXTS_PATH)
    position = (1200, 350)
    if message == '':
        text = ad_texts_in_store[np.random.randint(5)].strip().upper()
    else:
        if len(message.split(' ')) > 5:
            text = ' '.join(message.split(' ')[:5])
        else:
            text = message.strip().upper()
    font_scale = 3
    color = (255, 255, 255)
    thickness = 10
    font = cv2.FONT_HERSHEY_DUPLEX
    line_type = cv2.LINE_AA

    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    line_height = text_size[1] + 16
    x, y0 = position
    for i, line in enumerate(text.split(" ")):
        y = y0 + i * line_height
        merged = cv2.putText(merged,
                             line,
                             (x, y),
                             font,
                             font_scale,
                             color,
                             thickness,
                             line_type)

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    cv2.imwrite(OUTPUT_FILE, merged)