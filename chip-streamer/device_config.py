
class RangedValue:
    def __init__(self, _val, _min, _max):
        self.min = _min
        self.max = _max
        self.val = _min if _val < _min else (_max if _val > _max else _val)

    def set(self, _val):
        self.val = self.min if _val < self.min else (self.max if _val > self.max else _val)


class Led:
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
    width = 640
    height = 400

    def __init__(self, w, h):
        self.set(w, h)

    def set(self, w, h):
        self.width = w
        self.height = h


class Camera:

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

    def __init__(self):
        self.camera = Camera()
        self.leds = [Led(10, 20, 0)]
        self.name = 'Testcam'


dev = Device()