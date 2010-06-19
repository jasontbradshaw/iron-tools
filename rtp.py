import subprocess as sp
import threading
import time
import os

class RTPTools:
    def __init__(self):
        self.proc = None
        self.lock = threading.Lock()

    def isalive(self):
        if self.proc is None:
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
    
    def start(self, inputfile, address, port, start_time=None, end_time=None,
              wait_start=False):
        """
        Start the rtpplay process with a file to play, an address, then port
        to play to, an optional time to start playing the stream from, and
        whether to pause execution and wait after seeking to the start time.
        If wait_start is True, a call to begin_playback will be neccessary
        to actually start the playback.
        """
        
        with self.lock:
            # make sure file exists before running rtpplay
            if not os.path.isfile(inputfile):
                raise IOError("Input file '%s' not found." % inputfile)

            # only launch if process isn't already running or isn't alive
            if not self.isalive():
                args = ["./%s" % self.path,
                        "-f", inputfile]
                
                if start_time is not None:
                    args.extend(["-b", str(start_time)])
                
                if end_time is not None:
                    args.extend(["-e", str(end_time)])
                
                if wait_start:
                    args.append("-w")
                
                args.extend(["%s/%d" % (address, port)])
                
                # TODO: close devnull?
                DEVNULL = open(os.devnull, 'w')
                self.proc = sp.Popen(args, stderr=DEVNULL, stdout=DEVNULL,
                                     stdin=sp.PIPE)
        
        return self.pid()
    
    def begin_playback(self):
        """
        If rtpplay was started with waiting turned on, this sends the command
        to begin actual playback.  If waiting wasn't enabled, this
        command has no effect, ill or otherwise.
        """
        
        # send a newline to tell the process to start as soon as it can
        if self.isalive():
            self.proc.stdin.write("\n")

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

    def start(self, outputfile, address, port, dump_format="dump"):
        """
        Launches an rtpdump process with the already specified parameters.
        """
        
        with self.lock:
            # only launch if no process exists.
            if not self.isalive():
                
                args = ["./%s" % self.path,
                        "-F", dump_format,
                        "-o", outputfile,
                        "%s/%d" % (address, port)]
                
                # TODO: close devnull?
                DEVNULL = open(os.devnull, 'w')
                self.proc = sp.Popen(args, stderr=DEVNULL, stdout=DEVNULL)
        
        return self.pid()
