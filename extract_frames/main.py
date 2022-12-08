import argparse
import os


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


if __name__ == "__main__":
    main()
