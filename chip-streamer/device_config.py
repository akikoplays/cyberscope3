
class RangedValue:
    """
    Ranged value such that min < value < max.
    """

    def __init__(self, _val, _min, _max):
        """
        Initialize a value that is automatically clamped to min max.
        """
        self.min = _min
        self.max = _max
        self.val = self.set(_val)

    def set(self, _val):
        """
        Sets value clamped to min max.
        """
        self.val = self.min if _val < self.min else (self.max if _val > self.max else _val)


class Led:
    """
    Initialize an LED entity with given parameters.
    All params are ranged values, with ranges pre set by the class.
    """
    current = RangedValue(1, 0, 100)
    duration = RangedValue(1, 0, 40)
    type = RangedValue(0, 0, 3) #todo: define Led types (0:White, 1:UV, 2:RGB)

    def __init__(self, _current, _duration, _type):
        self.current.set(_current)
        self.duration.set(_duration)
        self.type.set(_type)

    def get_current(self):
        return self.current

    def get_duration(self):
        return self.duration

    def get_type(self):
        return self.type


class Resolution:
    """
    Initialize resolution entity, contains width and height of the image.
    """
    width = 640
    height = 400

    def __init__(self, w, h):
        self.set(w, h)

    def set(self, w, h):
        self.width = w
        self.height = h


class Camera:
    """
    Initialize camera entity that encompasses: resolution, shutter and TBD.
    Shutter is a RangedValue with preset boundaries.
    """
    def __init__(self):
        self.resolution = Resolution(640, 400)
        self.shutter = RangedValue(10, 0, 2000)

    def set_resolution(self, w, h):
        self.resolution.set(w, h)

    def get_resolution(self):
        return self.resolution

    def set_shutter(self, shutter):
        self.shutter.set(shutter)

    def get_shutter(self):
        return self.shutter


class Device:
    """
    Initialize a device entity, that encompasses:
    * camera
    * leds (list of #n led entities, depending on device type)
    * other params TBD
    """
    def __init__(self):
        self.camera = Camera()
        self.leds = [Led(10, 20, 0)]
        self.name = 'Testcam'


dev = Device()