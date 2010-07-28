import os

#Environment
ENV_DEV = "dev"
ENV_PRODUCTION = "prod"
ENVIRONMENT = ENV_DEV

#Shared Vars
SYNC_DIR = "sync"
DUMP_DIR = os.path.join(SYNC_DIR, "dump")

#Receiver config
RECEIVER_LOG_FILENAME = "receiver.log"
RTPPLAY_ADDRESS = "127.0.0.1"
RTPPLAY_PORT = 5008

#Recorder config
RECORDER_LOG_FILENAME = "recorder.log"
RTPDUMP_ADDRESS = "0.0.0.0"
RTPDUMP_PORT = 5006
RTPDUMP_PREVIEW_ADDRESS = "10.98.0.81"
RTPDUMP_PREVIEW_PORT = 5008

#Recorder strings
VIDEO_BASENAME = "_sermon"

if ENVIRONMENT == ENV_DEV:
    #Shared Vars
    SYNC_DIR = "sync"
    DUMP_DIR = os.path.join(SYNC_DIR, "dump")

    #Receiver config
    RECEIVER_LOG_FILENAME = "receiver.log"
    RTPPLAY_ADDRESS = "127.0.0.1"
    RTPPLAY_PORT = 5008

    #Recorder config
    RECORDER_LOG_FILENAME = "recorder.log"
    RTPDUMP_ADDRESS = "0.0.0.0"
    RTPDUMP_PORT = 5006
    RTPDUMP_PREVIEW_ADDRESS = "10.98.0.81"
    RTPDUMP_PREVIEW_PORT = 5008

    #Recorder strings
    VIDEO_BASENAME = "_sermon"

    #Shared strings
    FILE_NOT_FOUND = "could not find file '%s'."

elif ENVIRONMENT == ENV_PRODUCTION:
    #Shared Vars
    SYNC_DIR = "sync"
    DUMP_DIR = os.path.join(SYNC_DIR, "dump")

    #Receiver config
    RECEIVER_LOG_FILENAME = "receiver.log"
    RTPPLAY_ADDRESS = "127.0.0.1"
    RTPPLAY_PORT = 5008

    #Recorder config
    RECORDER_LOG_FILENAME = "recorder.log"
    RTPDUMP_ADDRESS = "0.0.0.0"
    RTPDUMP_PORT = 5006
    RTPDUMP_PREVIEW_ADDRESS = "10.98.0.81"
    RTPDUMP_PREVIEW_PORT = 5008

    #Recorder strings
    VIDEO_BASENAME = "_sermon"

    #Shared strings
    FILE_NOT_FOUND = "could not find file '%s'."

else:
    raise NotImplemented("'%s' not a supported environment." % ENVIRONMENT)

