import enum

class VideoFormat(enum.Enum):
    mp4 = 1
    webm = 2
    avi = 3
    mpeg = 4
    mpg = 5
    wmv = 6

def validate_format(format): 
    for f in VideoFormat:
        if f.name == format:
            return True
    return False


def get_codec(destination_format):
    if format == "webm":
        return "libvpx"
    
    if format == "wmv":
        return "wmv2"
    
    return "mpeg4"