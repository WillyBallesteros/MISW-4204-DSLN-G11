import enum

class VideoFormat(enum.Enum):
    MP4 = 1
    WEBM = 2
    AVI = 3
    MPEG = 4
    WMV = 5

def validate_format(format): 
    for f in VideoFormat:
        if f.name == format:
            return True
    return False