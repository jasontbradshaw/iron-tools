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
        
        # path to 'rtpplay' binary
        self.path = path
        self.proc = None

    def start(self, inputfile, address, port, start_time=0, end_time=None):
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
                        "-b", str(start_time),]
                if end_time:
                    args.extend(["-e", str(end_time)])
                args.extend(["%s/%d" % (address, port)])
                
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

    def __init__(self, path='rtpdump'):
        RTPTools.__init__(self)
        
        # path to 'rtpdump' binary
        self.path = path
        
        self.proc = None
        self.outputfile = ''

    def start(self, address, port, dump_format="dump", outputfile=None):
        """
        Launches an rtpdump process with the already specified parameters.
        """
        
        with self.lock:
            # only launch if no process exists.
            if not self.isalive():
                
                # timestamp the file if no file name was specified
                if not outputfile:
                    tm = time.strftime("%Y-%m-%d_%H-%M-%S.dump")
                else:
                    tm = outputfile
                
                args = ["./%s" % self.path,
                        "-F", dump_format,
                        "-o", tm,
                        "%s/%d" % (address, port)]
                
                # TODO: close devnull?
                DEVNULL = open(os.devnull, 'w')
                self.proc = sp.Popen(args, stderr=DEVNULL, stdout=DEVNULL)
                self.outputfile = outputfile
        
        return self.pid()
