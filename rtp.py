import subprocess as sp

class RTPDump:
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
        self.path = path
        self.dumpformat = dumpformat
        self.outputfile = outputfile

    def start(self):
        args = ["./%s" % self.path,
                "-F", self.dumpformat]
        if self.outputfile:
            args.extend(["-o", self.outputfile])
        args.append("%s/%d" % (self.address, self.port))

        self.proc = sp.Popen(args)
        return self.pid()
    
    def isalive(self):
        return self.proc.poll() is None

    def stop(self):
        self.proc.terminate()

    def pid(self):
        return self.proc.pid
