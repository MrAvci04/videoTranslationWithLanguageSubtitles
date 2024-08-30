
import os
import Application

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
video_path = "./input/test_input.mp4"
input_video = "test_input.mp4"
input_video_name = input_video.replace(".mp4", "")

# def run_whole_flow():
#     # Example usage
#     subtitle_file = './output/output_subtitles.srt'
#     output_file = 'output_with_subtitles.mp4'
#
#     SubtitlesMerger.merge_subtitles(video_path, subtitle_file, output_file)
#
#     print(f"Subtitles merged successfully into {output_file}")
#     # extracted_audio = extract_audio()
#     # language, segments = transcribe(extracted_audio)
#     # subtitle_file = generate_subtitle_file(language=language, segments=segments)
#     # add_subtitle_to_video(
#     #     soft_subtitle=True,
#     #     subtitle_file=subtitle_file,
#     #     subtitle_language=language
#     # )


if __name__ == '__main__':
    Application.initialize_app_with_gui()

    # audio_extract_from_video()  # WORKED SUCCESSFULLY
    # text = transcribe_audio_mp3("audio.mp3")  # WORKED SUCCESSFULLY
    # translate_text(text_to_translate=text, target_language='ar')  # WORKED SUCCESSFULLY
    #run_whole_flow()

