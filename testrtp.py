import os
import os.path
import rtp
import subprocess as sp


VLCCMD_OSX = '/Applications/VLC.app/Contents/MacOS/VLC'
VLCCMD_LINUX = 'vlc'

if os.uname()[0] == 'Darwin':
    VLCCMD = VLCCMD_OSX
elif os.uname()[0] == 'Linux':
    VLCCMD = VLCCMD_LINUX

def playdumpplay_test(infile='night.tsdump', outfile='playdumpplaytest.tsdump'):
    print 'begin play-dump-play test.'

    if not os.path.isfile(infile):
        print "infile '%s' does not exist. done." % infile
    if os.path.isfile(outfile):
        print "outfile '%s' exists; removing." % outfile
        os.remove(outfile)

    DEVNULL = open('/dev/null', 'w')
    play = rtp.RTPPlay('localhost', 9876, infile)
    dump = rtp.RTPDump('localhost', 9876, outfile)
    play2 = rtp.RTPPlay('localhost', 9000, outfile)

    print 'instantiated objects'

    print "press [enter] to start 'play'"
    raw_input()
    print "play pid:", play.start()
    print "press [enter] to start 'dump'"
    raw_input()
    print "dump pid:", dump.start()
    print "press [enter] to start 'play2'"
    raw_input()
    print "play2 pid:", play2.start()
    print "press [enter] to start 'vlc'"
    raw_input()
    args = [VLCCMD, 'rtp://@:9000']
    vlc = sp.Popen(args, stderr=DEVNULL, stdout=DEVNULL)

    while True:
        print "[enter] to view processes; 'q' to quit"
        i = raw_input()
        if i == 'q':
            break
        print 'play  alive:', play.isalive()
        print 'dump  alive:', dump.isalive()
        print 'play2 alive:', play2.isalive()
        print 'vlc   alive:', (vlc.poll() is None)

    play.stop()
    dump.stop()
    play2.stop()
    vlc.kill()
    print "killed processes"
    print "press [enter] to end"
    raw_input()

    print 'play  alive:', play.isalive()
    print 'dump  alive:', dump.isalive()
    print 'play2 alive:', play2.isalive()
    print 'vlc   alive:', (vlc.poll() is None) # is vlc alive?
    print 'done.'

if __name__ == "__main__":
    playdumpplay_test()
