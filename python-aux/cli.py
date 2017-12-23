import os
import os.path
import subprocess
import sys
import signal
import logging

def collect_files_of_type(root, extension):
    logging.debug("-- collecting files with extension: %s, from %s" % (extension, root))
    list = []
    for item in os.listdir(root):
        if os.path.isfile(os.path.join(root, item)):
            if item.endswith(extension):
                list.append(item)
                logging.debug(".... %s" % item)
    return list


def run_cli_async(cmdstr, queue=None):
    logging.debug("Running CLI async: %s" % cmdstr)

    try:
        proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
    except OSError as e:
        logging.debug("-- OSError > %s" % e.errno)
        logging.debug("-- OSError > %s" % e.strerror)
        logging.debug("-- OSError > %s" % e.filename)
    except KeyboardInterrupt as e:
        logging.debug('-- keyboard interrupt exception')
        exit(1)
    except:
        logging.debug('-- exception: %s' % sys.exc_info()[0])

    logging.debug('-- return code: %s' % proc.returncode)
    # In case this fn is called as a new thread, we can't just return value, that's why we use queue to store process data
    if (queue is not None):
        queue.put(proc)
    return proc


def run_cli_sync(cmdstr):
    logging.debug("Running CLI sync: %s" % cmdstr)
    ret = []
    try:
        proc = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
        for line in proc.stdout:
            print line
            ret.append(line)
        proc.wait()
    except OSError as e:
        logging.debug("-- OSError > %s" % e.errno)
        logging.debug("-- OSError > %s" % e.strerror)
        logging.debug("-- OSError > %s" % e.filename)
    except KeyboardInterrupt as e:
        logging.debug('-- keyboard interrupt exception')
        exit(1)
    except:
        logging.debug('-- exception: %s' % sys.exc_info()[0])

    logging.debug('-- return code: %s' % proc.returncode)
    return proc, ret


def kill_process(p):
    logging.debug('Killing process %s' % p)
    if p:
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
