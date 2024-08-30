import math

import speech_recognition as sr
from google.cloud.speech_v1 import RecognitionConfig
from pydub import AudioSegment
from google.cloud import speech
import datetime
# Initialize the recognizer
recognizer = sr.Recognizer()
wav_audio_file = './output/converted_audio.wav'


# def transcribe_audio(audio_file:str):
#     # Convert MP3 to WAV
#     audio = AudioSegment.from_mp3(audio_file)
#     audio.export('converted_audio.wav', format='wav')
#
#     with sr.AudioFile("converted_audio.wav") as source:
#         # Listen to the audio file and record it
#         audio_data = recognizer.record(source)
#
#         # Recognize (convert from speech to text)
#         try:
#             # text = recognizer.recognize_google_cloud(audio_data)
#             # print("google Transcription: ", text)
#
#             text = recognizer.recognize_whisper(audio_data)
#             # print("whisper Transcription: ", text)
#
#         except sr.UnknownValueError:
#             print("Whisper Recognition could not understand audio")
#         except sr.RequestError as e:
#             print(f"Could not request results from Whisper Recognition service; {e}")
#
#         return text


def transcribe_gcs(gcs_uri: str) -> str:
    """Asynchronously transcribes the audio file from Cloud Storage
    Args:
        gcs_uri: The Google Cloud Storage path to an audio file.
            E.g., "gs://storage-bucket/file.flac".
    Returns:
        The generated transcript from the audio file provided.
    """
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=44100,
        language_code="en-US",
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    transcript_builder = []
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        transcript_builder.append(f"\nTranscript: {result.alternatives[0].transcript}")
        transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")

    transcript = "".join(transcript_builder)
    print(transcript)

    return transcript


# Function to convert seconds to SRT time format
def format_time(seconds):

    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

    return formatted_time


def transcribe_and_generate_srt_file(audio_file: str):
    # Convert MP3 to WAV
    audio = AudioSegment.from_mp3(audio_file)
    audio.export(wav_audio_file, format='wav')
    # Open the audio file
    with sr.AudioFile(wav_audio_file) as source:
        audio_data = recognizer.record(source)

        # Recognize (convert from speech to text)
        try:
            # Perform the speech recognition
            full_text = recognizer.recognize_whisper(audio_data)

            # Split the text into chunks (for simplicity, let's assume a chunk per sentence)
            sentences = full_text.split('. ')

            # Initialize variables for the SRT file
            srt_content = []
            current_time = 0
            sentence_duration = len(audio_data.get_wav_data()) / len(sentences) / 1000  # Average duration per sentence

            for i, sentence in enumerate(sentences):
                start_time = format_time(current_time)
                end_time = format_time(current_time + sentence_duration)
                current_time += sentence_duration

                srt_content.append(f"{i + 1}")
                srt_content.append(f"{start_time} --> {end_time}")
                srt_content.append(sentence)
                srt_content.append("")  # Blank line between entries

            # Write the SRT content to a file
            with open('./output/output_subtitles.srt', 'w') as srt_file:
                srt_file.write("\n".join(srt_content))
            print("SRT file generated successfully!")

        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")

    return full_text
