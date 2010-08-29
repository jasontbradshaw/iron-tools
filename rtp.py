import subprocess as sp
import threading
import time
import os

class RTPTools:
    def __init__(self):
        self.proc = None
        self.lock = threading.Lock()

    def isalive(self):
        """
        Checks if the process is non-'None', and if so returns its
        poll status.
        """
        
        return self.proc is not None and self.proc.poll() is None
    
    def start(self):
        raise NotImplementedError("'start' method not implemented")

    def stop(self):
        """
        Kills the process launched by 'start'.
        """
        
        if self.isalive():
            self.proc.terminate()
    
    def pid(self):
        """
        Returns the process identifier of the process started by 'start'.
        """
        
        if self.proc:
            return self.proc.pid
        return None

class RTPPlay(RTPTools):
    """
    Streams an RTP dump file to a network address.
    """
    
    def __init__(self, path="rtpplay"):
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
              wait_start=False, skip_to_end=False, end_wait_time=None,
              use_network_timestamp=True):
        """
        Start the rtpplay process with a file to play, an address, a port
        to play to, an optional time to start playing the stream from, and
        whether to pause execution and wait after seeking to the start time.
        
        If wait_start is True, a call to 'begin_playback' will be neccessary
        to actually start the playback.

        skip_to_end - burn through all packets until we get to end; start
            playing at end.
        end_wait_time - if at end of file, interval (in seconds) between checking
            for new data.
        use_network_timestamp - replace the RTP timestamp with the the network
            timestamp.
        """
        
        with self.lock:
            # make sure file exists before running rtpplay
            if not os.path.exists(inputfile):
                raise IOError("Input file '%s' not found." % inputfile)

            # only launch if process isn't already running or isn't alive
            if not self.isalive():
                args = ["./%s" % self.path,
                        "-f", inputfile]
                
                if skip_to_end:
                    args.append("-x")
                else:
                    if start_time is not None:
                        args.extend(["-b", str(start_time)])
                    
                    if end_time is not None:
                        args.extend(["-e", str(end_time)])
                    
                    if wait_start:
                        args.append("-w")
                
                # NOTE: in rtpplay end_wait_time will not work without
                # use_network_timestamp
                if end_wait_time:
                    args.extend(["-t", str(end_wait_time)])
                
                if use_network_timestamp:
                    args.append("-T")
                
                # add address/port string
                args.extend(["%s/%d" % (address, port)])
        
                self.proc = sp.Popen(args, stdin=sp.PIPE)
            
        return self.pid()
    
    def stop(self):
        """
        Kills the process launched by 'start'.
        """
        
        # only kill the process if it's currently alive
        if self.isalive():
            self.proc.terminate()
        
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
    
    def __init__(self, path="rtpdump"):
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
                
                self.proc = sp.Popen(args)
        
        return self.pid()

class RTPPlayEmulator:
    """Emulate RTPPlay class."""

    def __init__(self):
        self.proc_running = False
        self.file_exists = os.path.exists

    def start(self, inputfile, address, port, start_time=None, end_time=None,
              wait_start=False, skip_to_end=False, end_wait_time=None,
              use_network_timestamp=True):
        if not self.file_exists(inputfile):
            raise IOError("Input file '%s' not found." % inputfile)

        self.proc_running = True
        return self.pid()
    
    def stop(self):
        self.proc_running = False

    def pid(self):
        return -1

    def isalive(self):
        return self.proc_running

    def begin_playback(self):
        pass

class RTPDumpEmulator:
    """Emulate RTPDump class."""

    def __init__(self):
        self.proc_running = False

    def start(self, outputfile, address, port, dump_format="dump"):
        self.proc_running = True
        return self.pid()

    def stop(self):
        self.proc_running = False

    def pid(self):
        if self.proc_running:
            return -1
        return None

    def isalive(self):
        return self.proc_running
