import moviepy.editor as mp

def convert_video(input, output, codec):
  try:
    video_clip = mp.VideoFileClip(input)
    video_clip.write_videofile(output, codec=codec)
    video_clip.close()
    return None
  except Exception as e:
    return e