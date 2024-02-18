from pygame import image, transform


def rotate_image(sprite, angle, position, with_alpha):
    rotated_image = transform.rotate(sprite, angle)
    rect = rotated_image.get_rect(center=sprite.get_rect(topleft=position).center)

    if with_alpha:
        return rotated_image, rect
    else:
        return rotated_image, rect


class ResourceManager:
    def __init__(self, path, convert):
        self.path = path
        self.convert = convert

    def load_sprite(self, file, with_alpha=True):
        img = image.load(f"{self.path}{file}")

        if not self.convert:
            return img

        if with_alpha:
            return image.load(f"{self.path}{file}").convert_alpha()
        else:
            return image.load(f"{self.path}{file}").convert()
