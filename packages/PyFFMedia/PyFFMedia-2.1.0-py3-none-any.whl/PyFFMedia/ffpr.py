# ffpr.py
# ---------

import subprocess
import os
import json


class ffpr:
    def __init__(self):
        self.ffprobe_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "bin", "ffprobe.exe"
        )

    def probe(self, input_file):
        command = [
            self.ffprobe_path,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            input_file,
        ]
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        return json.loads(result.stdout.decode("utf-8"))

    def pretty(self, info):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"General:")
        print(f"  File: {info['format']['filename']}")

        duration_seconds = float(info["format"]["duration"])
        minutes, seconds = divmod(duration_seconds, 60)
        print(f"  Duration: {int(minutes)}:{int(seconds)} min")

        print(
            f"  Bit rate: {int(info['format']['bit_rate']) / 1000} kbit/s"
        )  # Convert bps to kbps
        print(f"  Number of streams: {info['format']['nb_streams']}")

        for i, stream in enumerate(info["streams"]):
            print(f"\nStream {i}:")
            print(f"  Codec: {stream['codec_name']}")
            print(f"  Type: {stream['codec_type']}")
            if "tags" in stream:
                print(f"  Language: {stream['tags'].get('language', 'N/A')}")
            if stream["codec_type"] == "video":
                print(f"  Width: {stream.get('width', 'N/A')}")
                print(f"  Height: {stream.get('height', 'N/A')}")
                print(f"  Frame rate: {stream.get('r_frame_rate', 'N/A')}")
            elif stream["codec_type"] == "audio":
                print(f"  Sample rate: {stream.get('sample_rate', 'N/A')}")
                print(f"  Channels: {stream.get('channels', 'N/A')}")
