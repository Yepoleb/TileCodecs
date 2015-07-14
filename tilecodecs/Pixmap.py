class Pixmap(object):
    """
    Class for handling indexed pixel data (one value per pixel)
    """

    def __init__(self, dim, data=None):
        """
        Pixmap constructor

        Arguments:
        dim - Dimensions tuple (width, height)
        data - List of pixel data
        """
        self.width, self.height = dim
        self.size = self.width * self.height
        if data is None:
            self.pixels = [0] * self.size
        else:
            self.set_data(data)

    def set_data(self, data):
        """
        Sets the pixel data to a new list of values
        """
        if len(data) == self.size:
            self.pixels = list(data)
        else:
            raise ValueError(("Wrong image data size. Should be {}, is {}."
                .format(self.size, len(data))))

    def set_pixel(self, px, loc):
        """
        Sets a single pixel in the image

        Arguments:
        px - Pixel value
        loc - Location tuple (x, y)
        """
        x, y = loc
        pos = y * self.width + x
        self.pixels[pos] = px

    def get_pixel(self, loc):
        """
        Sets a single pixel in the image

        Arguments:
        loc - Coordinates tuple (x, y)
        """
        x, y = loc
        pos = y * self.width + x
        return self.pixels[pos]

    def flip_v(self):
        """
        Flips the image vertically.
        """
        newpm = Pixmap((self.width, self.height))
        for y in range(self.height):
            for x in range(self.width):
                newpm.set_pixel(self.get_pixel((x, y)), (x, self.height-1 - y))
        return newpm

    def flip_h(self):
        """
        Flips the image horizontally.
        """
        newpm = Pixmap((self.width, self.height))
        for y in range(self.height):
            for x in range(self.width):
                newpm.set_pixel(self.get_pixel((x, y)), (self.width-1 - x, y))
        return newpm

    def flip_ud(self):
        """
        Alias for flip_v because it's easier to remember for me
        """
        return self.flip_v()

    def flip_lr(self):
        """
        Alias for flip_h because it's easier to remember for me
        """
        return self.flip_h()

    def paste(self, pm, loc):
        """
        Pastes another pixmap at the given location

        Arguments:
        pm - Pixmap to paste
        loc - Location tuple (x, y)
        """
        x, y = loc
        for srcy in range(pm.height):
            for srcx in range(pm.width):
                srcpx = pm.get_pixel((srcx, srcy))
                self.set_pixel(srcpx, (x + srcx, y + srcy))

    def save(self, name, pixelchars):
        """
        Saves the image in an xpm-like format without a header

        Arguments:
        name - Filename to save as
        pixelchars - List of characters for each pixel value
        """
        out = open(name, "w")
        for y in range(self.height):
            for x in range(self.width):
                px = self.get_pixel((x, y))
                out.write(pixelchars[px])
            out.write("\n")
        out.close()
