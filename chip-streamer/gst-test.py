import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject
from gi.repository import Gst as gst


'''
The following 2 lines are required for gstreamer => 1.0 
to initialize the GObject.
'''

GObject.threads_init()
gst.init(None)

pipe = gst.Pipeline()
src = gst.ElementFactory.make('videotestsrc', 'video')
enc = gst.ElementFactory.make('jpegenc', 'encoder')
pay = gst.ElementFactory.make('rtpjpegpay', 'rtp')
sink = gst.ElementFactory.make('udpsink', 'sink')

if not pipe:
    print('pipe fail')

if not src:
    print('src fail')

if not enc:
    print('enc fail')

if not pay:
    print('pay fail')

if not sink:
    print('sink fail')

# Ensure all elements were created successfully.
if (not pipe or not src or not enc or not pay or not sink):
    print('Not all elements could be created.')
    exit(-1)

sink.set_property('host', 'hiroshima.local')
sink.set_property('port', 5000)

pipe.add(src)
pipe.add(enc)
pipe.add(pay)
pipe.add(sink)

src.link(enc)
enc.link(pay)
pay.link(sink)

pipe.set_state(gst.State.PLAYING)

bus = pipe.get_bus()

msg = bus.timed_pop_filtered(gst.CLOCK_TIME_NONE, gst.MessageType.ERROR | gst.MessageType.EOS)
print msg

pipe.set_status(gst.State.NULL)

