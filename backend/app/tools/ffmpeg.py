import subprocess
import re
import json
import os
import math
import logging
import tempfile
from typing import Tuple

logger = logging.getLogger(__name__)


QUICKTIME_STRING = "mov,mp4,m4a,3gp,3g2,mj2"

MIMETYPES = {
    "webm": "video/webm",
    "ogg": "audio/ogg",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    QUICKTIME_STRING: "audio/quicktime",
}


def _ffprobe(filename: str):
    process = subprocess.Popen(
        [
            "ffprobe",
            "-hide_banner",
            "-loglevel",
            "fatal",
            "-show_error",
            "-show_format",
            "-print_format",
            "json",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    # print(" ".join(process.args))
    stdout, _stderr = process.communicate()
    output = json.loads(stdout)
    if "format" in output:
        return output["format"]
    else:
        raise Exception(f"ffprobe failed: {repr(output)}")


def get_duration(probe):
    duration = probe.get("duration")
    if duration is None:
        raise Exception("Duration not found in file")
    try:
        duration = float(duration)
    except ValueError:
        raise Exception(f"Invalid duration returned by ffprobe: {duration}")
    if not math.isfinite(duration):
        raise Exception(f"Invalud duration returned by ffprobe: {duration}")
    return duration


def check_and_fix_audio(filename, do_not_check=False) -> Tuple[str, float]:
    logger.info("Checking filename: %s", filename)
    probe = _ffprobe(filename)

    format_name = probe.get("format_name")
    if format_name == "matroska,webm":
        format_name = "webm"
        if "duration" not in probe:
            # Webm come without header, lets try to add header
            tmp_filename = filename + ".convert.webm"
            try:
                try:
                    subprocess.check_call(
                        [
                            "ffmpeg",
                            "-i",
                            filename,
                            "-vcodec",
                            "copy",
                            "-acodec",
                            "copy",
                            tmp_filename,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except Exception as _e:
                    raise Exception("Adding header to webm failed")
                probe = _ffprobe(tmp_filename)
                os.rename(tmp_filename, filename)
            finally:
                if os.path.isfile(tmp_filename):
                    os.remove(tmp_filename)
    elif (
        format_name not in ("wav", "ogg", QUICKTIME_STRING, "mp3") and not do_not_check
    ):
        raise Exception(f"Unsuported audio format: {format_name}")
    logger.info("File detected as %s", format_name)
    return format_name, get_duration(probe)


def convert_to_mp3(data: bytes) -> bytes:
    p = subprocess.Popen(
        ["ffmpeg", "-i", "pipe:", "-codec:a", "libmp3lame", "-f", "mp3", "pipe:1"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    result, _err = p.communicate(data)
    if len(result) < 200:
        # Conversion failed as it may need data from the end, we first write file into file
        with tempfile.NamedTemporaryFile() as f:
            f.write(data)
            f.flush()
            p = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i",
                    f.name,
                    "-codec:a",
                    "libmp3lame",
                    "-f",
                    "mp3",
                    "pipe:1",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            result, _err = p.communicate()
    return result
