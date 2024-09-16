import moviepy.editor as mp
from gtts import gTTS
import os

def create_youtube_short(post_title, post_content, background_video_path, output_path):
    # Generate text-to-speech audio
    tts = gTTS(text=post_content, lang='en', slow=False)
    temp_audio_path = "temp_audio.mp3"
    tts.save(temp_audio_path)
    
    # Load the audio file
    audio_clip = mp.AudioFileClip(temp_audio_path)
    
    # Load the background video
    background_clip = mp.VideoFileClip(background_video_path)
    
    # Trim the background video to exactly 30 seconds
    background_clip = background_clip.subclip(0, 30)
    
    # Resize the background video to 9:16 aspect ratio (1080x1920 for high quality)
    background_clip = background_clip.resize(height=1920)
    background_clip = background_clip.crop(x_center=background_clip.w/2, y_center=background_clip.h/2, width=1080, height=1920)
    
    # Create text clips
    title_clip = mp.TextClip(post_title, fontsize=40, color='white', font='Arial', size=(1000, None), method='caption')
    title_clip = title_clip.set_position(('center', 100)).set_duration(30)
    
    # Overlay the clips
    final_clip = mp.CompositeVideoClip([background_clip, title_clip])
    
    # Set the audio
    final_clip = final_clip.set_audio(audio_clip)
    
    # Write the result to a file
    final_clip.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac')
    
    # Clean up temporary audio file
    os.remove(temp_audio_path)
