"""
_image_funcs.py
14. June 2023

General image tools

Author:
Nilusink
"""
from warnings import warn
import pygame as pg
import typing as tp

try:
    # noinspection PyUnresolvedReferences
    from PIL import Image, ImageDraw
    PIL_EXISTS = True

except ImportError:
    PIL_EXISTS = False


if PIL_EXISTS:
    def merge_alphas(
            a: Image,
            b: Image,
            opr: tp.Callable[[float, float], float]
    ) -> Image:
        """
        merge the alpha channels of two images

        :param a: first alpha
        :param b: second alpha
        :param opr: operation to merge the channels
        """
        if not PIL_EXISTS:
            raise ImportError(
                "PIL needs to be installed to use the Image widget.\n"
                "\tto install PIL, use\n"
                "\t\t\"pip install pillow\""
            )

        im_a = a.load()
        im_b = b.load()
        width, height = a.size

        alpha = Image.new('L', (width, height))
        im: tp.Any = alpha.load()
        for x in range(width):
            for y in range(height):
                im[x, y] = opr(im_a[x, y], im_b[x, y])

        return alpha


    def add_corners(
            im: Image,
            ulr: int,
            urr: int,
            llr: int,
            lrr: int
    ) -> Image:
        """
        adds corners to an image

        :param im: input image
        :param ulr: upper left radius
        :param urr: upper right radius
        :param llr: lower left radius
        :param lrr: lower right radius
        :returns: the converted image
        """
        if not PIL_EXISTS:
            raise ImportError(
                "PIL needs to be installed to use the Image widget.\n"
                "\tto install PIL, use\n"
                "\t\t\"pip install pillow\""
            )

        alpha = Image.new('L', im.size, 255)
        w, h = im.size

        # upper left corner
        ulc = Image.new("L", (ulr * 2, ulr * 2), 0)
        draw = ImageDraw.Draw(ulc)
        draw.ellipse((0, 0, ulr * 2 - 1, ulr * 2 - 1), fill=255)
        ulc = ulc.crop((0, 0, ulr, urr))
        alpha.paste(ulc, (0, 0))

        # upper right corner
        urc = Image.new("L", (urr * 2, urr * 2), 0)
        draw = ImageDraw.Draw(urc)
        draw.ellipse((0, 0, urr * 2 - 1, urr * 2 - 1), fill=255)
        urc = urc.crop((urr, 0, 2 * urr, urr))
        alpha.paste(urc, (w - urr, 0))

        # lower left radius
        llc = Image.new("L", (llr * 2, llr * 2), 0)
        draw = ImageDraw.Draw(llc)
        draw.ellipse((0, 0, llr * 2 - 1, llr * 2 - 1), fill=255)
        llc = llc.crop((0, llr, llr, llr * 2))
        alpha.paste(llc, (0, h - llr))

        # lower right radius
        lrc = Image.new("L", (lrr * 2, lrr * 2), 0)
        draw = ImageDraw.Draw(lrc)
        draw.ellipse((0, 0, lrr * 2 - 1, lrr * 2 - 1), fill=255)
        lrc = lrc.crop((lrr, lrr, lrr * 2, lrr * 2))
        alpha.paste(lrc, (w - lrr, h - lrr))

        # apply the corner radius, keeping the image's alpha (if already present)
        *rgb, ia = im.split()  # extract alpha channel from image

        # check if the image even has an alpha channel
        if len(rgb) < 3:
            im.putalpha(alpha)  # if not, just put the calculated mask on the image

        else:
            im.putalpha(merge_alphas(alpha, ia, min))

        return im


    def pil_image_to_surface(pil_image):
        """
        helper function for converting pillow images to pygame images
        """
        return pg.image.fromstring(
            pil_image.tobytes(),
            pil_image.size,
            pil_image.mode
        ).convert_alpha()

else:
    warn("PIL is not installed, some functionality is limited!")
