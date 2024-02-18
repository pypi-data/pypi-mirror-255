# __init__.py

from .ffmpeg_script import ffpe, ffpr

import os

def add_ffmpeg_to_path():
    ffmpeg_path = os.path.join(os.path.dirname(__file__), '..', 'bin')
    os.environ['PATH'] += os.pathsep + ffmpeg_path

add_ffmpeg_to_path()
