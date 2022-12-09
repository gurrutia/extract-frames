# Extract Frames

Small Python CLI tool that extracts frames from video file as `.jpg` images.

Frames are saved to a unique subdirectory created in same directory as the video.

---

## Installation

```sh
pip install git+https://github.com/gurrutia/extract-frames.git
```

---

## Usage

```sh
extract-frames --help
```

```sh
usage: extract-frames [-h] [-f] [-s] [-e] path   

Extract frames from video as .jpg images

positional arguments:
  path            path to video with extension   

options:
  -h, --help      show this help message and exit
  -f , --frames   split every n frame(s)
  -s , --start    start timestamp, or n representing seconds from     
                  start
  -e , --end      end timestamp, or n representing seconds from       
                  start
```

---

## Examples

_**Assume**_ `video.mp4` _**is 2 minutes long, 30 fps.**_

Extract every frame from `video.mp4`:

```sh
extract-frames ../path/to/video.mp4
```

**3,600 images saved to**: `../path/to/video_frames_split_every_1_frame_between_0_3600`

---

Extract every `5` frames between `0:50` and `1:10` from `video.mp4` _(4 ways)_:

```sh
extract-frames ../path/to/video.mp4 -f 5 -s 0:50 -e 1:10
extract-frames ../path/to/video.mp4 -f 5 -s 50 -e 70
extract-frames ../path/to/video.mp4 --frames 5 --start 0:50 --end 1:10
extract-frames ../path/to/video.mp4 --frames 5 --start 50 --end 70
```

**120 images saved to**: `../path/to/video_frames_split_every_5_frames_between_300_900`

---

## Used by

- **Grand St. Settlement** _(non-profit)_ filmmaking instructors to gather film stills that aid in constructing lesson plans for their youth workshops. [See a workshop example here.](extras/GSS_Filmmaking_Fall_2022_Transfiguration_Schools_W1.pdf)
