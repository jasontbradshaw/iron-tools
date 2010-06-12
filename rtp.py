import subprocess as sp
import threading
import time
import os

class RTPTools:
    def __init__(self):
        self.proc = None
        self.lock = threading.Lock()

    def isalive(self):
        if not self.proc:
            return False
        return self.proc.poll() is None

    def start(self):
        raise NotImplementedError("start not implemented")

    def stop(self):
        """
        Kills the process launched by 'start'.
        """
        
        if not self.isalive():
            return
        self.proc.terminate()

    def pid(self):
        """
        Returns the process identifier of the process started by 'start'.
        """
        
        if not self.proc:
            return None
        return self.proc.pid

class RTPPlay(RTPTools):
    """
    Streams an RTP dump file to a network address.
    """
    
    def __init__(self, path='rtpplay'):
        """
        Builds an RTPPlay object, optionally with the path to the binary
        rtpplay file.
        """

        # init parent for its precious methodly fluids
        RTPTools.__init__(self)
        
        # path to 'rtpplay' executable
        self.path = path
        self.proc = None

    def start(self, inputfile, address, port, start_time=0):
        """
        Start the rtpplay process with a file to play, an address, then port
        to play to, and optionally a time to start playing the stream from.
        """
        
        with self.lock:
            # make sure file exists before running rtpplay
            if not os.path.isfile(inputfile):
                raise IOError("Input file '%s' not found." % inputfile)

            # only launch if process isn't already running or isn't alive
            if not self.isalive():
                args = ["./%s" % self.path,
                        "-f", inputfile,
                        "-b", str(starttime),
                        "%s/%d" % (address, port)]

                # TODO: figure out how to pipe stderr crap properly w/o
                # screwing up our test.
                # TODO: close devnull?
                DEVNULL = open(os.devnull, 'w')
                self.proc = sp.Popen(args, stderr=DEVNULL, stdout=DEVNULL)
        
        return self.pid()

class RTPDump(RTPTools):
    """
    Dumps an RTP stream to a file.
    """
    
    # TODO:
    # - allow user to append to existing file
    # - backup files
    # - what happens if a rtpdump is already running?
    #   - kill it.
    #   - what about the existing file? TODO.

    def __init__(self, address='localhost', port=9876, outputfile=None, dumpformat='dump',
            path='rtpdump'):

        RTPTools.__init__(self)

        self.proc = None

        self.address = address
        self.port = port
        self.dumpformat = dumpformat
        self.outputfile = outputfile
        self.path = path

    def start(self):
        """
        Launches an rtpdump process with the already specified parameters.
        """
        
        with self.lock:
            # only launch if no process exists.
            if not self.isalive():
                
                # timestamp the file if no file name was specified
                if not self.outputfile:
                    tm = time.strftime("%Y-%m-%d_%H-%M-%S.dump")
                else:
                    tm = self.outputfile
                
                args = ["./%s" % self.path,
                        "-F", self.dumpformat,
                        "-o", tm,
                        "%s/%d" % (self.address, self.port)]
                
                # TODO: close devnull?
                DEVNULL = open(os.devnull, 'w')
                self.proc = sp.Popen(args, stderr=DEVNULL, stdout=DEVNULL)
        
        return self.pid()
