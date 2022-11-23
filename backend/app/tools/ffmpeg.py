import subprocess
import re


def get_duration(filename):
    process = subprocess.Popen(
        ["ffmpeg", "-i", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout, _stderr = process.communicate()
    matches = re.search(
        r"Duration:\s*(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),",
        stdout.decode(),
        re.DOTALL,
    )
    if matches is None:
        raise Exception(f"Invalid file: {filename}")

    matches = matches.groupdict()

    return (
        float(matches["hours"]) * 60 * 60
        + float(matches["minutes"]) * 60
        + float(matches["seconds"])
    )
