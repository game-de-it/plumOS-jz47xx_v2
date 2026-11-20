#!/usr/bin/env python3
"""Build a signed JZ47xx runtime package from explicitly named files."""

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

MAX_BYTES = 256 * 1024 * 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--revision", type=int, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("files", nargs="+", help="Paths relative to the runtime root")
    args = parser.parse_args()
    if not 1 <= args.revision <= 999999999 or len(args.files) > 256:
        parser.error("revision or file count is out of range")
    if len(set(args.files)) != len(args.files):
        parser.error("duplicate payload path")

    root = args.runtime.resolve(strict=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as tmp:
        tmp = Path(tmp)
        payload = tmp / "payload"
        signature = tmp / "signature"
        with payload.open("wb") as stream:
            stream.write(f"PLUMOS-JZ47XX-RUNTIME-1\n{args.revision}\n".encode("ascii"))
            for name in sorted(args.files):
                relative = Path(name)
                path = root / relative
                if (relative.as_posix() != name or relative.is_absolute()
                        or ".." in relative.parts or path.resolve() != path
                        or not path.is_file() or not all(c.isascii() and
                            (c.isalnum() or c in "_-.+/") for c in name)
                        or len(name) >= 200):
                    parser.error(f"invalid payload path {name!r}")
                size = path.stat().st_size
                if not size or stream.tell() + size + 256 > MAX_BYTES:
                    parser.error(f"empty file or payload exceeds size limit at {name!r}")
                stream.write(f"{name}\t{size}\n".encode("ascii"))
                with path.open("rb") as source:
                    shutil.copyfileobj(source, stream)
        subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(args.key),
                        "-out", str(signature), str(payload)], check=True)
        result = tmp / "package"
        with result.open("wb") as stream:
            stream.write(signature.read_bytes())
            with payload.open("rb") as source:
                shutil.copyfileobj(source, stream)
        result.replace(args.output)


if __name__ == "__main__":
    main()
