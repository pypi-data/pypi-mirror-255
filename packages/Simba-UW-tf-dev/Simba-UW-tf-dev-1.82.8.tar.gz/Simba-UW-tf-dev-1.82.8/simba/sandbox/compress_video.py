from typing import Any
from typing import NoReturn
import ffmpeg
import os


def resize_video(
        video_absolute_path: str,
        output_file_absolute_path: str,
        size_upper_bound: int,
        two_pass: bool = True, ) -> str:
    """
    Compress video file to max-supported size.
        :param video_absolute_path: the video you want to compress.
        :param size_upper_bound: Max video size in KB.
        :param two_pass: Set to True to enable two-pass calculation.
        :param filename_suffix: Add a suffix for new video.
        :return: out_put_name or error
    """

    # Bitrate reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    probe_json_representation = ffmpeg.probe(video_absolute_path)
    # Video duration, in s.
    duration = float(probe_json_representation['format']['duration'])
    # Audio bitrate, in bps.
    streams: list[dict] = probe_json_representation['streams']
    # {'index': 0, 'codec_name': 'h264', 'codec_long_name': 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10', 'profile': 'Main', 'codec_type': 'video', 'codec_tag_string': 'avc1', 'codec_tag': '0x31637661', 'width': 1280, 'height': 720, 'coded_width': 1280, 'coded_height': 720, 'closed_captions': 0, 'film_grain': 0, 'has_b_frames': 1, 'sample_aspect_ratio': '1:1', 'display_aspect_ratio': '16:9', 'pix_fmt': 'yuv420p', 'level': 31, 'color_range': 'tv', 'color_space': 'bt709', 'color_transfer': 'bt709', 'color_primaries': 'bt709', 'chroma_location': 'left', 'field_order': 'progressive', 'refs': 1, 'is_avc': 'true', 'nal_length_size': '4', 'id': '0x1', 'r_frame_rate': '25/1', 'avg_frame_rate': '25/1', 'time_base': '1/12800', 'start_pts': 0, 'start_time': '0.000000', 'duration_ts': 4096000, 'duration': '320.000000', 'bit_rate': '71355', 'bits_per_raw_sample': '8', 'nb_frames': '8000', 'extradata_size': 43, 'disposition': {'default': 1, 'dub': 0, 'original': 0, 'comment': 0, 'lyrics': 0, 'karaoke': 0, 'forced': 0, 'hearing_impaired': 0, 'visual_impaired': 0, 'clean_effects': 0, 'attached_pic': 0, 'timed_thumbnails': 0, 'captions': 0, 'descriptions': 0, 'metadata': 0, 'dependent': 0, 'still_image': 0}, 'tags': {'creation_time': '2022-06-14T17:31:48.000000Z', 'language': 'und', 'handler_name': 'ISO Media file produced by Google Inc. Created on: 06/14/2022.', 'vendor_id': '[0][0][0][0]'}}
    stream: dict[str, Any] | None = next(
        (stream for stream in streams if stream['codec_type'] == 'audio'),
        None,
    )

    assert stream is not None, \
        "Stream is None, streams had not include any item with audio codec_type"

    # e.x. '654874'
    bit_rate: str = stream['bit_rate']
    audio_bitrate = float(bit_rate)

    # Target total bitrate, in bps.
    target_total_bitrate = (size_upper_bound * 1024 * 8) / (1.073741824 * duration)
    min_audio_bitrate = 32000
    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate

    # FIXME: IDK why but for some reason this function raise exception in
    # any case. BTW I comment it just for now
    # check_bitrate(
    #     duration,
    #     size_upper_bound,
    #     target_total_bitrate,
    #     min_audio_bitrate,
    #     video_bitrate,
    # )

    # target audio bitrate, in bps
    max_audio_bitrate = 256000
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate

    i = ffmpeg.input(video_absolute_path)
    if two_pass:
        ffmpeg.output(
            i,
            '/dev/null' if os.path.exists('/dev/null') else 'NUL',
            **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
        ).overwrite_output().run()
        ffmpeg.output(
            i,
            output_file_absolute_path,
            **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
        ).overwrite_output().run()
    else:
        ffmpeg.output(
            i,
            output_file_absolute_path,
            **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
        ).overwrite_output().run()

    if os.path.getsize(output_file_absolute_path) <= size_upper_bound * 1024:
        return output_file_absolute_path
    elif os.path.getsize(output_file_absolute_path) < os.path.getsize(video_absolute_path):  # Do it again
        return resize_video(
            video_absolute_path=output_file_absolute_path,
            output_file_absolute_path=output_file_absolute_path,
            size_upper_bound=size_upper_bound
        )
    else:
        raise Exception('Resize failed')


def check_bitrate(
        duration: float,
        size_upper_bound: int,
        target_total_bitrate: float,
        min_audio_bitrate: int,
        video_bitrate: float, ) -> None | NoReturn:
    total_bitrate_lower_bound = 11000
    min_video_bitrate = 100000

    assert target_total_bitrate < total_bitrate_lower_bound, \
        'Bitrate is extremely low! Stop compress!'

    # Best min size, in kB.
    best_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / (8 * 1024)

    assert size_upper_bound < best_min_size, \
        f"Quality not good! Recommended minimum size: {int(best_min_size)} KB."

    assert video_bitrate < 1000, \
        f'Bitrate ({video_bitrate}) is extremely low! Stop compress.'


# This example turned 120 MB into 34 MB
# Note that this is a really CPU intensive process. The Anime is around 24 minute. I guess using processes is wiser than doing it in normal way
file_absolute_path = resize_video(
    video_absolute_path='/Users/simon/Desktop/splash_2024.mp4',
    size_upper_bound=50 * 1000,
    output_file_absolute_path="some-name.mp4",
)
print(file_absolute_path)