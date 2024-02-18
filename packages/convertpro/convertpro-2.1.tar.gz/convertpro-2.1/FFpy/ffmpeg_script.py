# ffmpeg_script.py
import sys
import subprocess

def run_executable(executable, *args):
    try:
        subprocess.run([executable] + list(args), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {executable}: {e}")
        sys.exit(1)

def ffpe(*args):
    run_executable("ffmpeg", *args)

def ffpr(*args):
    run_executable("ffprobe", *args)
