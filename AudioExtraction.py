import ffmpeg


def extract_audio(input_video_name, input_video_path):
    extracted_audio = f"audio-{input_video_name}.wav"
    stream = ffmpeg.input(input_video_path)
    stream = ffmpeg.output(stream, extracted_audio)
    ffmpeg.run(stream, overwrite_output=True)
    return extracted_audio