# ffpe.py
# ---------

import os
import gc
import subprocess
from functools import lru_cache


class ffpe:
    def __init__(self):
        self.ffmpeg_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "bin", "ffmpeg.exe"
        )

    @lru_cache(maxsize=None)
    def convert(
        self,
        input_file,
        output_file,
        cv=None,
        ca=None,
        s=None,
        hwaccel=None,
        ar=None,
        ac=None,
        ba=None,
        r=None,
        f=None,
    ):
        command = [self.ffmpeg_path]

        if hwaccel:
            command += ["-hwaccel", hwaccel]

        command += ["-i", input_file]

        if cv:
            command += ["-c:v", cv]
        if ca:
            command += ["-c:a", ca]
        if s:
            command += ["-s", s]
        if ar:
            command += ["-ar", str(ar)]
        if ac:
            command += ["-ac", str(ac)]
        if ba:
            command += ["-b:a", str(ba)]
        if r:
            command += ["-r", str(r)]
        if f:
            command += ["-f", f]

        command += ["-y", output_file]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg command failed with error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        # Call the garbage collector
        gc.collect()

    def codecs(self):
        command = [self.ffmpeg_path, "-codecs"]
        try:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )
            output = result.stdout.decode("utf-8")
            lines = output.split("\n")
            print("{:<20} {:<25} {:<60}".format("Codec", "Type", "Description"))
            print("{:<20} {:<25} {:<60}".format("-----", "----", "-----------"))
            for line in lines[11:]:  # Skip the header lines
                if line:  # Skip empty lines
                    fields = line.split()
                    if len(fields) >= 4:  # Ensure there are enough fields
                        codec_name = fields[1]
                        codec_type = fields[2].strip("()")
                        codec_description = " ".join(fields[3:])
                        print(
                            "{:<20} {:<25} {:<60}".format(
                                codec_name, codec_type, codec_description
                            )
                        )
                        print("-" * 150)  # Print a line
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg command failed with error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        gc.collect()

    def formats(self):
        command = [self.ffmpeg_path, "-formats"]
        try:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )
            output = result.stdout.decode("utf-8")
            lines = output.split("\n")
            print("{:<30} {:<80}".format("Format", "Description"))
            print("{:<30} {:<80}".format("------", "-----------"))
            for line in lines[5:]:  # Skip the header lines
                if line:  # Skip empty lines
                    fields = line.split()
                    if len(fields) >= 2:  # Ensure there are enough fields
                        format_name = fields[1]
                        format_description = " ".join(fields[2:])
                        print("{:<30} {:<80}".format(format_name, format_description))
                        print("-" * 100)  # Print a line
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg command failed with error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        gc.collect()
