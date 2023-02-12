from app.tools.ffmpeg import _ffprobe, check_and_fix_audio
import pytest


def test_probe_webm(test_webm, test_wav):
    probe = _ffprobe(test_webm)
    assert probe["format_name"] == "matroska,webm"

    probe = _ffprobe(test_wav)
    assert probe["format_name"] == "wav"


def test_check_and_fix_audio(test_webm, test_wav):
    output = check_and_fix_audio(test_webm)
    assert ("webm", pytest.approx(2.279)) == output

    output = check_and_fix_audio(test_wav)
    assert ("wav", pytest.approx(0.418)) == output
