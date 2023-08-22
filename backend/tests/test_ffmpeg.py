from app.tools.ffmpeg import (
    _ffprobe,
    check_and_fix_audio,
    QUICKTIME_STRING,
    convert_to_mp3,
)
import pytest


def test_probe(test_webm, test_wav, test_ogg, test_mov, test_mp3):
    probe = _ffprobe(test_webm)
    assert probe["format_name"] == "matroska,webm"

    probe = _ffprobe(test_wav)
    assert probe["format_name"] == "wav"

    probe = _ffprobe(test_ogg)
    assert probe["format_name"] == "ogg"

    probe = _ffprobe(test_mov)
    assert probe["format_name"] == QUICKTIME_STRING

    probe = _ffprobe(test_mp3)
    assert probe["format_name"] == "mp3"


def test_check_and_fix_audio(test_webm, test_wav, test_ogg, test_mp3):
    output = check_and_fix_audio(test_webm)
    assert ("webm", pytest.approx(2.279)) == output

    output = check_and_fix_audio(test_wav)
    assert ("wav", pytest.approx(0.418)) == output

    output = check_and_fix_audio(test_ogg)
    assert ("ogg", pytest.approx(2.003833)) == output

    output = check_and_fix_audio(test_mp3)
    assert ("mp3", pytest.approx(0.417938)) == output


def test_convert_to_mp3(test_ogg):
    with open(test_ogg, "rb") as f:
        data = f.read()
    result = convert_to_mp3(data)
    assert result[:3] == b"ID3"
