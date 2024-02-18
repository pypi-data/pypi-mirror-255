import argparse
from pathlib import Path

from shrink_img import shrink_image_buffer


parser = argparse.ArgumentParser()
parser.add_argument("src")
parser.add_argument("max_size", help="WxH")
parser.add_argument("dest")

args = parser.parse_args()

src_data = Path(args.src).resolve().read_bytes()
max_width, max_height = [int(s) for s in args.max_size.split("x")]
dest_data = shrink_image_buffer(src_data, max_width, max_height)
Path(args.dest).resolve().write_bytes(dest_data)
