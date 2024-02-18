import numpy as np
from PIL import Image


def split_quadrants(matrix):
    res = np.split(matrix, 2, axis=1)
    [q1, q3] = np.split(res[0], 2)
    [q2, q4] = np.split(res[1], 2)
    return q1, q2, q3, q4


def join_matrix(q1, q2, q3, q4):
    q1, q2, q3, q4 = q4, q3, q2, q1
    return np.append(np.append(q1, q2, axis=1), np.append(q3, q4, axis=1), axis=0)


def img_scram(img):
    if img.shape == (1, 1):
        return img
    q1, q2, q3, q4 = split_quadrants(img)
    q1 = img_scram(q1)
    q2 = img_scram(q2)
    q3 = img_scram(q3)
    q4 = img_scram(q4)
    return np.rot90(join_matrix(q1, q2, q3, q4))


def img_rescram(img):
    if img.shape == (1, 1):
        return img
    q1, q2, q3, q4 = split_quadrants(img)
    q1 = img_rescram(q1)
    q2 = img_rescram(q2)
    q3 = img_rescram(q3)
    q4 = img_rescram(q4)
    return np.rot90(join_matrix(q1, q2, q3, q4), -1)


def scram(image, iterations=10):
    image = img_scram(image)
    Image.fromarray(image).save("Semi.png")
    height, width = image.shape
    new_image = np.zeros_like(image)
    for _ in range(iterations):
        for y in range(height):
            for x in range(width):
                new_x = (3 * x + 4 * y) % width
                new_y = (2 * x + 3 * y) % height
                new_image[new_y, new_x] = image[y, x]
        image = new_image.copy()
    return Image.fromarray(new_image)


def unscram(image, iterations=10):
    height, width = image.shape
    new_image = np.zeros_like(image)
    for _ in range(iterations):
        for y in range(height):
            for x in range(width):
                new_x = (3 * x - 4 * y) % width
                new_y = (-2 * x + 3 * y) % height
                new_image[new_y, new_x] = image[y, x]
        image = new_image.copy()
    new_image = img_rescram(new_image)
    return Image.fromarray(new_image)
