import subprocess as sp

class RTPTools:
    def __init__(self):
        self.proc = None

    def isalive(self):
        return self.proc.poll() is None

    def start(self):
        pass

    def stop(self):
        self.proc.terminate()

    def pid(self):
        return self.proc.pid

class RTPPlay(RTPTools):
    def __init__(self, address, port, inputfile=None, begintime=0,
            path='rtpplay'):
        self.proc = None

        self.address = address
        self.port = port
        self.inputfile = inputfile
        self.begintime = begintime
        self.path = path

    def start(self):
        if not self.proc:
            args = ["./%s" % self.path,
                    "-f", self.inputfile,
                    "-b", str(self.begintime),
                    "%s/%d" % (self.address, self.port),
                   ]

            self.proc = sp.Popen(args)
        return self.pid()


class RTPDump(RTPTools):
    # TODO:
    # - allow user to append to existing file
    # - backup files
    # - what happens if a rtpdump is already running?
    #   - kill it.
    #   - what about the existing file? TODO.

    def __init__(self, address, port, outputfile=None, dumpformat='dump',
            path='rtpdump'):
        self.proc = None

        self.address = address
        self.port = port
        self.dumpformat = dumpformat
        self.outputfile = outputfile
        self.path = path

    def start(self):
        if not self.proc:
            args = ["./%s" % self.path,
                    "-F", self.dumpformat]
            if self.outputfile:
                args.extend(["-o", self.outputfile])
            args.append("%s/%d" % (self.address, self.port))

            self.proc = sp.Popen(args)
        return self.pid()

