import argparse
import os
import sys
from dataclasses import dataclass

import cv2


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
    frames_dirname = f"{video.filename}_frames_splitby({video.splitby})"
    framesdir = os.path.join(video.dirname, frames_dirname)
    if os.path.exists(framesdir):
        i = 1
        while os.path.exists(framesdir):
            dir = os.path.join(video.dirname, f"{frames_dirname} ({i})")

    os.mkdir(framesdir)

    return framesdir


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
        default=0,
        metavar="",
        help="end timestamp, or n representing seconds from start",
    )
    args = parser.parse_args()
    video_metadata = build_video_metadata(args)


if __name__ == "__main__":
    main()
