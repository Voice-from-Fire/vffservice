from app.tools.ffmpeg import _ffprobe, check_and_fix_audio
import pytest


def test_probe(test_webm, test_wav, test_ogg):
    probe = _ffprobe(test_webm)
    assert probe["format_name"] == "matroska,webm"

    probe = _ffprobe(test_wav)
    assert probe["format_name"] == "wav"

    probe = _ffprobe(test_ogg)
    assert probe["format_name"] == "ogg"


def test_check_and_fix_audio(test_webm, test_wav, test_ogg):
    output = check_and_fix_audio(test_webm)
    assert ("webm", pytest.approx(2.279)) == output

    output = check_and_fix_audio(test_wav)
    assert ("wav", pytest.approx(0.418)) == output

    output = check_and_fix_audio(test_ogg)
    assert ("ogg", pytest.approx(2.003833)) == output
