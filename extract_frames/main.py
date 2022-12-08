import argparse
import os


def valid_path(p: str) -> str:
    if not os.path.isfile(p):
        raise argparse.ArgumentTypeError(f"File not found, got {p!r}")

    if not os.path.isabs(p):
        p = os.path.abspath(p)

    return p


def positive_int(s: str) -> int:
    try:
        v = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Expected integer, got {s!r}")

    if v <= 0:
        raise argparse.ArgumentTypeError(f"Expected positive integer, got {v}")

    return v


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
    args = parser.parse_args()


if __name__ == "__main__":
    main()
