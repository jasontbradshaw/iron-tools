import os

# environment
ENV_DEV = "dev"
ENV_PRODUCTION = "prod"
ENVIRONMENT = ENV_DEV

# flask
RECORDER_HOST = "0.0.0.0"
RECORDER_PORT = 5081
PLAYBACK_HOST = "0.0.0.0"
PLAYBACK_PORT = 5082

# shared vars
SYNC_DIR = "sync"
DUMP_DIR = os.path.join(SYNC_DIR, "dump")
MAX_BLOCK_TIME = 3

# playback config
PLAYBACK_LOG_FILENAME = "playback.log"
RTPPLAY_ADDRESS = "127.0.0.1"
RTPPLAY_PORT = 5008

# recorder config
RECORDER_LOG_FILENAME = "recorder.log"
RTPDUMP_ADDRESS = "0.0.0.0"
RTPDUMP_PORT = 5006
RTPDUMP_PREVIEW_ADDRESS = "127.0.0.1"
RTPDUMP_PREVIEW_PORT = 5008

# recorder strings
VIDEO_BASENAME = "_sermon"
VIDEO_FILE_EXT = "dump"
COMMIT_FILE_EXT = "time"

# development environment
if ENVIRONMENT == ENV_DEV:
    
    RTPPLAY_ADDRESS = "127.0.0.1"
    RTPPLAY_PORT = 5008
    
    RTPDUMP_ADDRESS = "0.0.0.0"
    RTPDUMP_PORT = 5006
    RTPDUMP_PREVIEW_ADDRESS = "127.0.0.1"
    RTPDUMP_PREVIEW_PORT = 5008

# production environment
elif ENVIRONMENT == ENV_PRODUCTION:
    
    RTPPLAY_ADDRESS = "10.97.0.81"
    RTPPLAY_PORT = 5008
    
    RTPDUMP_ADDRESS = "0.0.0.0"
    RTPDUMP_PORT = 5006
    RTPDUMP_PREVIEW_ADDRESS = "10.98.0.81"
    RTPDUMP_PREVIEW_PORT = 5008
    
    SYNC_DIR = "/video/hi_res/test1"
    DUMP_DIR = os.path.join(SYNC_DIR, "dump")
    
    RECORDER_PORT = 80
    PLAYBACK_PORT = 80

else:
    raise NotImplemented("'%s' not a supported environment." % ENVIRONMENT)
