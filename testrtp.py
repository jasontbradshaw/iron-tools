import os
import os.path
import rtp
import subprocess as sp
import time


VLCCMD_OSX = '/Applications/VLC.app/Contents/MacOS/VLC'
VLCCMD_LINUX = 'vlc'

if os.uname()[0] == 'Darwin':
    VLCCMD = VLCCMD_OSX
elif os.uname()[0] == 'Linux':
    VLCCMD = VLCCMD_LINUX

def playpreview_test(samplefile='night.tsdump', outfile='playpreviewtest.dump'):
    print 'begin playpreviewtest'
    play = rtp.RTPPlay()

    print "play pid:", play.start(samplefile, 'localhost', 9876)
    print "buffering..."
    time.sleep(2)
    print "go to /start_record"
    print "go to /play_preview/0"
    print "press [enter] to start vlc"
    raw_input()
    args = [VLCCMD, 'rtp://@:10000']
    DEVNULL = open(os.devnull, 'w')
    vlc = sp.Popen(args, stderr=DEVNULL, stdout=DEVNULL)
    print "press [enter] to stop"
    raw_input()
    play.stop()
    vlc.kill()
    print 'done'

def vlcdumpplay_test(outfile='vlcdumpplay.dump'):
    print 'begin vlcdumpplay test'
    print 'i assume vlc is streaming a video to 127.0.0.1:9876'
    print 'press [enter] if this is true'
    raw_input()
    DEVNULL = open(os.devnull, 'w')
    dump = rtp.RTPDump()
    play = rtp.RTPPlay()

    print "dump pid:", dump.start(outfile, 'localhost', 9876)
    time.sleep(2)
    print "play pid:", play.start(outfile, 'localhost', 9000)
    print "press [enter] to start 'vlc'"
    raw_input()
    args = [VLCCMD, 'rtp://@:9000']
    vlc = sp.Popen(args, stderr=DEVNULL, stdout=DEVNULL)

    print "press [enter] to quit"
    raw_input()
    dump.stop()
    play.stop()
    vlc.kill()
    print 'done'


def playdumpplay_test(infile='night.tsdump', outfile='playdumpplaytest.tsdump'):
    print 'begin play-dump-play test.'
    print """
+---------+                 ###########                 ###########
|original | ==============> # rtpdump # =============>  #   vlc   #
|dump     |    rtpplay      ###########    rtpplay      ###########
+---------+    @:9876                      @:9000
"""

    if not os.path.isfile(infile):
        print "infile '%s' does not exist. done." % infile
    if os.path.isfile(outfile):
        print "outfile '%s' exists; removing." % outfile
        os.remove(outfile)

    DEVNULL = open(os.devnull, 'w')
    play = rtp.RTPPlay()
    dump = rtp.RTPDump()
    play2 = rtp.RTPPlay()

    print 'instantiated objects'
    time.sleep(1)
    print "play pid:", play.start(infile, 'localhost', 9876)
    time.sleep(2)
    print "dump pid:", dump.start(outfile, 'localhost', 9876)
    time.sleep(2)
    print "play2 pid:", play2.start(outfile, 'localhost', 9000)
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
    try:
        vlc.kill()
    except:
        print "failed to kill vlc. oh well."

    print "killing processes"
    time.sleep(2)

    print 'play  alive:', play.isalive()
    print 'dump  alive:', dump.isalive()
    print 'play2 alive:', play2.isalive()
    print 'vlc   alive:', (vlc.poll() is None) # is vlc alive?
    print 'done.'

if __name__ == "__main__":
    tests = [playdumpplay_test, vlcdumpplay_test, playpreview_test]
    s = ''
    for i, t in enumerate(tests):
        s += "[%d] %s\n" % (i, t.__name__)
    s += "choose: "
    choice = int(raw_input(s))

    tests[choice]()
