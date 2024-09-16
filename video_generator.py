from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import os

def generate_short_video(audio_path, output_path):
    # Load the subway surfers video
    video = VideoFileClip("assets/subway_surfers.mp4").without_audio().subclip(0, 32)
    
    # Load the generated audio
    audio = AudioFileClip(audio_path)
    
    # If the audio is longer than the video, trim it
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)
    
    # Set the audio of the video
    video = video.set_audio(audio)
    
    # Write the result to a file
    video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    
    # Close the clips
    video.close()
    audio.close()

def generate_long_video(audio_paths, output_path):
    # Load the long subway surfers video
    long_video = VideoFileClip("assets/subway_surfers_long.mp4").without_audio()
    
    video_clips = []
    current_time = 0
    
    for audio_path in audio_paths:
        # Load the generated audio
        audio = AudioFileClip(audio_path)
        
        # Extract a portion of the long video
        video_clip = long_video.subclip(current_time, current_time + audio.duration)
        
        # Set the audio of the video clip
        video_clip = video_clip.set_audio(audio)
        
        video_clips.append(video_clip)
        current_time += audio.duration
    
    # Concatenate all video clips
    final_video = concatenate_videoclips(video_clips)
    
    # Write the result to a file
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    
    # Close the clips
    long_video.close()
    final_video.close()
    for clip in video_clips:
        clip.close()

if __name__ == "__main__":
    # This code will run if you execute this script directly
    # It's useful for testing the video generation functions
    audio_path = "output/audios/test_audio.mp3"
    output_path = "output/videos/test_output.mp4"
    generate_short_video(audio_path, output_path)
