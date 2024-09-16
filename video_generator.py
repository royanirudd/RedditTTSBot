from moviepy.editor import VideoFileClip, AudioFileClip
import os

def generate_video(audio_path, output_path):
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

if __name__ == "__main__":
    # This code will run if you execute this script directly
    # It's useful for testing the video generation function
    audio_path = "output/audios/test_audio.mp3"
    output_path = "output/videos/test_output.mp4"
    generate_video(audio_path, output_path)
