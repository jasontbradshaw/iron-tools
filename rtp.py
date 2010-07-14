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
        
        return self.proc and self.proc.poll() is None

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
        rtpplay file and the name of the armed flag file.
        """

        # init parent for its precious methodly fluids
        RTPTools.__init__(self)
        
        # path to 'rtpplay' binary
        self.path = path
        self.proc = None

        self.pollrtpplay = None
        
    def start(self, inputfile, address, port, start_time=None, end_time=None,
              wait_start=False):
        """
        Start the rtpplay process with a file to play, an address, a port
        to play to, an optional time to start playing the stream from, and
        whether to pause execution and wait after seeking to the start time.
        
        If wait_start is True, a call to 'begin_playback' will be neccessary
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
                
                # add address/port string
                args.extend(["%s/%d" % (address, port)])
        
                # TODO: close devnull?
                DEVNULL = open(os.devnull, 'w')
                self.proc = sp.Popen(args, stderr=DEVNULL, stdout=sp.PIPE,
                                     stdin=sp.PIPE)
                self.start_poll(self.proc.stdout) 
                
        return self.pid()
    
    def start_poll(self, stdoutpipe):
        if self.pollrtpplay and self.pollrtpplay.is_alive():
            self.pollrtpplay.kill = True
            self.pollrtpplay.join()
        self.pollrtpplay = PollRTPPlay(stdoutpipe)
        self.pollrtpplay.start()

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
    
    def is_armed(self):
        """
        Determines if the currently armed file is done being armed.  Returns
        'True' if this is the case, and 'False' if nothing has been played
        yet or the file can't be found.
        """

        return self.pollrtpplay.is_alive() and self.pollrtpplay.armed
    
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

class PollRTPPlay(threading.Thread):
    def __init__(self, stdout_pipe,
            armed_text = "Press enter to begin playback."):
        threading.Thread.__init__(self)
        self.armed = False
        self.pipe = stdout_pipe
        self.armed_text = armed_text
        self.kill = False
        self.daemon = True

    def run(self):
        while not self.kill:
            time.sleep(0.1)
            line = self.pipe.read()
            if self.armed_text in line:
                self.armed = True

