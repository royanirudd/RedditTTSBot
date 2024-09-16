import moviepy.editor as mp
from pydub import AudioSegment

def generate_short_video(audio_path, output_path):
    # Load the background video
    background = mp.VideoFileClip("assets/subway_surfers.mp4")
    
    # Load the audio
    audio = mp.AudioFileClip(audio_path)
    
    # Set the duration of the video to match the audio
    video = background.subclip(0, audio.duration)
    
    # Set the audio of the video
    final_video = video.set_audio(audio)
    
    # Write the result to a file
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

def generate_long_video(audio_paths, output_path):
    # Load the background video
    background = mp.VideoFileClip("assets/subway_surfers_long.mp4")
    
    # Load the comment audio
    comment_audio = AudioSegment.from_mp3("assets/comment_who_is_ahole.mp3")
    
    # Load the like and subscribe audio
    like_subscribe_audio = AudioSegment.from_mp3("assets/like_and_subscribe.mp3")
    
    # Combine all audio files
    combined_audio = AudioSegment.empty()
    for i, audio_path in enumerate(audio_paths):
        audio = AudioSegment.from_mp3(audio_path)
        combined_audio += audio
        if i < len(audio_paths) - 1:  # Don't add comment audio after the last post
            combined_audio += comment_audio

    # Add like and subscribe audio at the end
    combined_audio += like_subscribe_audio
    
    # Export the combined audio to a temporary file
    temp_audio_path = "temp_combined_audio.mp3"
    combined_audio.export(temp_audio_path, format="mp3")
    
    # Load the combined audio as a MoviePy audio clip
    audio = mp.AudioFileClip(temp_audio_path)
    
    # Set the duration of the video to match the audio
    video = background.subclip(0, audio.duration)
    
    # Set the audio of the video
    final_video = video.set_audio(audio)
    
    # Write the result to a file
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    # Clean up the temporary audio file
    import os
    os.remove(temp_audio_path)
