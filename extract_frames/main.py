import argparse
import math
import os
import sys
from dataclasses import dataclass

import cv2
from tqdm import tqdm


@dataclass
class Video:
    path: str
    dirname: str
    basename: str
    filename: str
    framecount: int
    fps: int
    splitby: int
    start: int
    end: int


def valid_path(p: str) -> str:
    if not os.path.isfile(p):
        raise argparse.ArgumentTypeError(f"File not found, got {p!r}")

    if not os.path.isabs(p):
        p = os.path.abspath(p)

    return p


def positive_int(s: str, allow_zero=False, msg=None) -> int:
    try:
        n = int(s)
    except ValueError:
        msg = f"Expected integer, got {s!r}" if msg is None else msg
        raise argparse.ArgumentTypeError(msg)

    if allow_zero and n < 0 or not allow_zero and n <= 0:
        msg = f"Expected positive integer, got {n}" if msg is None else msg
        raise argparse.ArgumentTypeError(msg)

    return n


def timestamp_in_seconds(ts: str) -> int:
    error_msg = f"Invalid timestamp, got {ts!r}"
    if ":" in ts:
        seconds = 0
        for value in ts.split(":"):
            if len(value) > 2:
                raise argparse.ArgumentTypeError(error_msg)

            n = positive_int(value, allow_zero=True, msg=error_msg)
            if n >= 60:
                raise argparse.ArgumentTypeError(error_msg)

            try:
                seconds = seconds * 60 + int(value, 10)
            except ValueError:
                raise argparse.ArgumentTypeError(error_msg)
    else:
        seconds = positive_int(ts, allow_zero=True, msg=error_msg)

    return seconds


def video_details(videopath: str) -> tuple[int, int]:
    video_capture = cv2.VideoCapture(videopath)
    if not video_capture.isOpened():
        raise IOError(f"Unable to open video, got '{videopath}'")

    framecount = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    video_capture.release()

    return framecount, fps


def validate_start_end(
    args: argparse.Namespace, framecount: int, fps: int
) -> tuple[int, int]:
    start = args.start * fps if args.start != 0 else 0
    if start > framecount:
        raise ValueError(f"Start timestamp exceeds video length, got {args.start}")

    end = args.end * fps if args.end is not None else framecount
    end = framecount if end > framecount else end
    if end == start:
        raise ValueError(f"End timestamp equal to start timestamp, got {args.end}")
    if end < start:
        raise ValueError(f"End timestamp prior to start timestamp, got {args.end}")

    return start, end


def build_video_metadata(args: argparse.Namespace) -> Video:
    dirname = os.path.dirname(args.path)
    basename = os.path.basename(args.path)
    filename = os.path.splitext(basename)[0]
    framecount, fps = video_details(args.path)

    try:
        start, end = validate_start_end(args, framecount, fps)
    except ValueError as e:
        print(f"TimestampError: {e}")
        sys.exit(1)

    return Video(
        path=args.path,
        dirname=dirname,
        basename=basename,
        filename=filename,
        framecount=framecount,
        fps=fps,
        splitby=args.splitby,
        start=start,
        end=end,
    )


def make_framesdir(video: Video) -> str:
    frame_text = "frame" if video.splitby == 1 else "frames"
    frames_dirname = f"{video.filename}_frames_split_every_{video.splitby}_{frame_text}_between_{video.start}_{video.end}"
    framesdir = os.path.join(video.dirname, frames_dirname)
    if os.path.exists(framesdir):
        i = 1
        while os.path.exists(framesdir):
            framesdir = os.path.join(video.dirname, f"{frames_dirname} ({i})")
            i += 1

    os.mkdir(framesdir)

    return framesdir


def extract_frames(video: Video) -> None:
    frames_expected = math.ceil((video.end - video.start) / video.splitby)
    video_capture = cv2.VideoCapture(video.path)
    next_frame = video.start
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, next_frame)
    framesdir = make_framesdir(video)

    with tqdm(total=frames_expected) as pbar:
        i = 1
        while video_capture.isOpened():
            success, img = video_capture.read()
            if success:
                imgpath = os.path.join(framesdir, f"frame{next_frame}.jpg")
                cv2.imwrite(imgpath, img)
                pbar.update()

                if frames_expected == i:
                    video_capture.release()
                    break
                i += 1

                next_frame += video.splitby
                if video.splitby != 1:
                    video_capture.set(cv2.CAP_PROP_POS_FRAMES, next_frame)
            else:
                video_capture.release()
                break

    print(f"\nFrames directory: {framesdir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="extract-frames", description="Extract frames from video as .jpg image"
    )
    parser.add_argument("path", type=valid_path, help="path to video with extension")
    parser.add_argument(
        "-f",
        "--frames",
        type=positive_int,
        default=1,
        metavar="",
        help="split every n frame(s)",
        dest="splitby",
    )
    parser.add_argument(
        "-s",
        "--start",
        type=timestamp_in_seconds,
        default=0,
        metavar="",
        help="start timestamp, or n representing seconds from start",
    )
    parser.add_argument(
        "-e",
        "--end",
        type=timestamp_in_seconds,
        metavar="",
        help="end timestamp, or n representing seconds from start",
    )
    args = parser.parse_args()
    video_metadata = build_video_metadata(args)
    extract_frames(video_metadata)


if __name__ == "__main__":
    main()
