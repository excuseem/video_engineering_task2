#!/usr/bin/env python3
import argparse
import subprocess


def transcode(source, target, idr_interval, encoder):
    encoders_map = {
        "nvenc_h264": " -c:v h264_nvenc",
        "qsv_h264": " -c:v h264_qsv",
        "libx264": " -c:v libx264",
    }
    encoder_option = encoders_map.get(encoder, " -c:v libx264")
    idr_option = f" -force_key_frames \"expr:gte(t,n_forced*{idr_interval})\"" if idr_interval else ""

    ffmpeg_command = f"""
    ffmpeg -re -i "{source}"{encoder_option}{idr_option} -vf "drawtext=text='%{{localtime\\:%Y-%m-%d %H\\\\:%M\\\\:%S}}':x=10:y=10:fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5" \
    -map 0 -b:v:0 5000k -s:v:0 1920x1080 -map 0 -b:v:1 2500k -s:v:1 1280x720 -map 0 -b:v:2 1000k -s:v:2 854x480 \
    -use_timeline 1 -use_template 1 -window_size 5 -adaptation_sets "id=0,streams=v id=1,streams=a" -f dash "{target}"
    """

    process = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error: {stderr.decode('utf-8')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcode a video to Low Latency MPEG-DASH stream.")
    parser.add_argument("-source", required=True, help="Source URL or file")
    parser.add_argument("-target", required=True, help="Target master.mpd file")
    parser.add_argument("-idr", type=int, default=2, help="Custom pattern to set I-frames every X seconds")
    parser.add_argument("-encoder", choices=["libx264", "nvenc_h264", "qsv_h264"], default="libx264", help="Encoder to use")

    args = parser.parse_args()
    transcode(args.source, args.target, args.idr, args.encoder)
