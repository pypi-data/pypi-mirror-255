# ffmpeg_script.py
import sys
import subprocess

def run_executable(executable):
    try:
        subprocess.run([executable] + sys.argv[1:], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {executable}: {e}")
        sys.exit(1)

def ffpe():
    run_executable("ffmpeg")

def ffpr():
    run_executable("ffprobe")
