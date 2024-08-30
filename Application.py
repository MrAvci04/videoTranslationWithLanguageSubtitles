import tkinter as tk
import time
from tkinter.filedialog import askopenfilename
from tkinter import TOP
import cv2
import os
from googletrans import Translator
import AudioExtraction
import SpeechRecogntion
import math
import ffmpeg

from audio_extract import extract_audio
from faster_whisper import WhisperModel

import TextTranslation

translator = Translator()
video_path = "./input/test_input.mp4"
input_video_name = "test_input"
extracted_audio_file = "./output/extracted_audio.mp3"


def initialize_app_with_gui():
    window = tk.Tk()

    greeting = tk.Label(text="Hello, Upload video to translate! Press 'q' to exit the video")
    greeting.pack()

    entry = tk.Entry(window, width=60)
    entry.pack()
    buttons = tk.Frame(window)
    buttons.pack(pady=5)
    button1 = tk.Button(buttons, text="Upload mp4 file", command=handle_upload_file)
    button1.pack(side=TOP)
    button2 = tk.Button(buttons, text="Arabic Translation", command=handle_arabic_translation)
    button2.pack(side=TOP)
    button3 = tk.Button(buttons, text="Hebrew Translation", command=handle_hebrew_translation)
    button3.pack(side=TOP)
    button2 = tk.Button(buttons, text="Arabic subtitles", command=handle_arabic_subtitles)
    button2.pack(side=TOP)
    button3 = tk.Button(buttons, text="Hebrew subtitles", command=handle_hebrew_subtitles)
    button3.pack(side=TOP)
    window.mainloop()


def handle_upload_file():
    print("Please select your file")
    time.sleep(1)
    video_path = askopenfilename()
    input_video_name = video_path.split('/')[-1].replace(".mp4", "")
    file_name = video_path.split("/")[-1]
    print(file_name)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
    else:
        # Read and display the video frame by frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Display the frame
            cv2.imshow('Video', frame)

            # Press 'q' to exit the video
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        # Release the video capture object and close all OpenCV windows
        cap.release()
        cv2.destroyAllWindows()


def audio_extract_from_video():
    extracted_audio_file = AudioExtraction.extract_audio(
        input_video_name=input_video_name,
        input_video_path=video_path)


def create_srt(subtitles, output_file):
    """
    Create an SRT file from the translated subtitles list.

    Args:
    subtitles (list of dict): List of dictionaries containing subtitle info.
    output_file (str): Path to the output SRT file.
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        for idx, subtitle in enumerate(subtitles, start=1):
            start_time = format_time(subtitle['start'])
            end_time = format_time(subtitle['end'])
            text = subtitle['text']

            file.write(f"{idx} \n")
            file.write(f"{start_time} --> {end_time}\n")
            file.write(f"{text}\n\n")


def handle_arabic_subtitles():
    extracted_audio = extract_audio_subtitles()

    language, segments = transcribe(audio=extracted_audio)
    translated_segments = TextTranslation.translate_segments(segments, 'ar')
    # Save translated subtitles to SRT
    translated_subtitle_file = './output/translated_subtitles_ar.srt'
    create_srt(translated_segments, translated_subtitle_file)

    output_video = './output/output_video_with_ar_subtitles.mp4'
    # Add subtitles using ffmpeg-python
    ffmpeg.input(video_path).output(output_video, vf=f'subtitles={translated_subtitle_file}').run()


def handle_hebrew_subtitles():
    extracted_audio = extract_audio_subtitles()
    language, segments = transcribe(audio=extracted_audio)
    translated_segments = TextTranslation.translate_segments(segments, 'he')

    # Save translated subtitles to SRT
    translated_subtitle_file = './output/translated_subtitles_he.srt'
    create_srt(translated_segments, translated_subtitle_file)

    output_video = './output/output_video_with_he_subtitles.mp4'
    # Add subtitles using ffmpeg-python
    ffmpeg.input(video_path).output(output_video, vf=f'subtitles={translated_subtitle_file}').run()


def handle_arabic_translation():
    print("Arabic translation button was clicked!")
    # Check if the file exists
    if os.path.exists(extracted_audio_file):
        os.remove(extracted_audio_file)

    extract_audio(input_path=video_path, output_path=extracted_audio_file)

    text = transcribe_audio_mp3(extracted_audio_file)
    # google_cloud_translate_text(text, 'ar')
    translate_text(text, 'ar')


def handle_hebrew_translation():
    print("Hebrew translation was clicked!")

    # Check if the file exists
    if os.path.exists(extracted_audio_file):
        os.remove(extracted_audio_file)

    extract_audio(input_path=video_path, output_path=extracted_audio_file)
    text = transcribe_audio_mp3(extracted_audio_file)
    # google_cloud_translate_text(text, 'he')
    translate_text(text, 'he')


def transcribe_audio_mp3(file_name: str):
    text = SpeechRecogntion.transcribe_and_generate_srt_file(file_name)
    #SpeechRecogntion.generate_srt_file()
    # SpeechRecogntion.transcribe_gcs("gs://realtime-transcription/audio.mp3") # WORKED
    return text


def translate_text(text_to_translate: str, target_language: str):

    # Translate from English to target language
    translation = translator.translate(text_to_translate, src='en', dest=target_language)

    # Print the translated text
    print(f"Original Text: {text_to_translate}")
    print(f"Translated Text: {translation.text}")


def extract_audio_subtitles():
    stream = ffmpeg.input(video_path)
    stream = ffmpeg.output(stream, extracted_audio_file)
    ffmpeg.run(stream, overwrite_output=True)
    return extracted_audio_file


def transcribe(audio):
    model = WhisperModel("small")
    segments, info = model.transcribe(audio)
    language = info[0]
    print("Transcription language", info[0])
    segments = list(segments)
    for segment in segments:
        # print(segment)
        print("[%.2fs -> %.2fs] %s" %
              (segment.start, segment.end, segment.text))
    return language, segments


def format_time(seconds):

    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

    return formatted_time


def generate_subtitle_file(language, segments):
    subtitle_file = f"./output/sub-{input_video_name}.{language}.srt"
    text = ""
    for index, segment in enumerate(segments):
        segment_start = format_time(segment.start)
        segment_end = format_time(segment.end)
        text += f"{str(index + 1)} \n"
        text += f"{segment_start} --> {segment_end} \n"
        text += f"{segment.text} \n"
        text += "\n"

    f = open(subtitle_file, "w")
    f.write(text)
    f.close()

    return subtitle_file


def add_subtitle_to_video(soft_subtitle, subtitle_file,  subtitle_language):

    video_input_stream = ffmpeg.input(video_path)
    subtitle_input_stream = ffmpeg.input(subtitle_file)
    output_video = f"./output/output-{input_video_name}.mp4"
    subtitle_track_title = subtitle_file.replace(".srt", "")

    if soft_subtitle:
        stream = ffmpeg.output(
            video_input_stream, subtitle_input_stream, output_video, **{"c": "copy", "c:s": "mov_text"},
            **{"metadata:s:s:0": f"language={subtitle_language}",
            "metadata:s:s:0": f"title={subtitle_track_title}"}
        )
        ffmpeg.run(stream, overwrite_output=True)

