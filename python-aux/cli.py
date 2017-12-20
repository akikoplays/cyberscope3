import os
import os.path
import subprocess
import sys
import signal


def collect_files_of_type(root, extension):

    print "-- collecting files with extension: %s" % (extension)
    list = []
    for item in os.listdir(root):
        if os.path.isfile(os.path.join(root, item)):
            if item.endswith(extension):
                list.append(item)
                print ".... %s" % (item)
    return list


def run_cli_async(cmdstr, queue=None):
    print "Running CLI async: ", cmdstr

    try:
        proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
    except OSError as e:
        print "-- OSError > ", e.errno
        print "-- OSError > ", e.strerror
        print "-- OSError > ", e.filename
    except KeyboardInterrupt as e:
        print '-- keyboard interrupt exception'
        exit(1)
    except:
        print '-- exception: ', sys.exc_info()[0]

    print '-- return code: %s' % proc.returncode
    # In case this fn is called as a new thread, we can't just return value, that's why we use queue to store process data
    if (queue is not None):
        queue.put(proc)
    return proc


def run_cli_sync(cmdstr):
    print "Running CLI sync: ", cmdstr
    ret = []
    try:
        proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
        for line in proc.stdout:
            print line
            ret.append(line)
        proc.wait()
    except OSError as e:
        print "-- OSError > ", e.errno
        print "-- OSError > ", e.strerror
        print "-- OSError > ", e.filename
    except KeyboardInterrupt as e:
        print '-- keyboard interrupt exception'
        exit(1)
    except:
        print '-- unknown exception: ', sys.exc_info()[0]

    print '-- return code: %s' % proc.returncode
    return proc, ret


def kill_process(p):
    print 'Killing process ', p
    if p:
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
