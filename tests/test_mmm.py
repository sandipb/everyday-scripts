from everyday_scripts.mmm import find_files
import pytest
from pathlib import Path
import itertools
import os
from pprint import pprint

def test_find_files(tmp_path):
    src: Path = tmp_path / "pictures"
    images: Path = tmp_path / "images"
    videos: Path = tmp_path / "videos"
    src.mkdir()
    images.mkdir()
    videos.mkdir()
    photo_files =  [
        "a/b/c/1.jpg",
        "a/b/2.PNG",
        "a/b/d/e/3.gif",
    ]
    video_files =  [
        "a/b/v1.mp4",
        "a/b/d/v1.MOV",
        "a/d/e/g/v3.avi",
    ]
    for pfile in itertools.chain(photo_files, video_files):
        f: Path = src / pfile
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("NULL")
    
    all_outs = [
        os.path.join(str(images), p)
        for p in photo_files
    ] + [
        os.path.join(str(videos), p)
        for p in video_files
    ]

    all_outs.sort()
    dmap = {"image": str(images), "video": str(videos)}
    got = [
        d for s, d in find_files(str(src), dest_map=dmap)
    ]
    got.sort()

    assert all_outs == got