import subprocess
import re
import json
import os
import math


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


def check_and_fix_audio(filename) -> float:
    probe = _ffprobe(filename)

    format_name = probe.get("format_name")
    if format_name == "matroska,webm":
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
    elif format_name not in ("wav",):
        raise Exception(f"Unsuported audio format: {format_name}")
    return get_duration(probe)
