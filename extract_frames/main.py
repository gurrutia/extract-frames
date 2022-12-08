import argparse
import os


def valid_path(p: str) -> str:
    if not os.path.isfile(p):
        raise argparse.ArgumentTypeError(f"File not found, got {p!r}")

    if not os.path.isabs(p):
        p = os.path.abspath(p)

    return p


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="extract-frames", description="Extract frames from video as .jpg image"
    )
    parser.add_argument("path", type=valid_path, help="path to video with extension")
    args = parser.parse_args()


if __name__ == "__main__":
    main()
