#!/usr/bin/env python3

import argparse
import os.path
from pathlib import Path
import subprocess
import sys


COMPILER = "gcc"


def _c_compile(source_path, output_path):
    """
    source_path assumed to exist
    """
    with open(source_path) as file:
        link_math = "<math.h>" in file.read()
               
    compiling_cmd = [
        COMPILER,
        "--output", output_path,
        "-Wall",
        source_path,
        ]
    if link_math:
        compiling_cmd.insert(1, "-lm")
    print(f"INFO: running {' '.join(map(str, compiling_cmd))}")
    compiling_proc = subprocess.run(compiling_cmd)
    return compiling_proc.returncode


def c_compile(raw_args=None):
    if raw_args is None:
        raw_args = sys.argv[1:]
    arg_parser = argparse.ArgumentParser(
        description="Compile C programs.",
        )
    arg_parser.add_argument(
        "file",
        type=Path,
        help="C source code path",
        )
    args = arg_parser.parse_args(raw_args)

    source_path = args.file.resolve()
    if not source_path.exists():
        print(f"ERROR: file {source_path} doesn't exist", file=sys.stderr)
        return 1

    output_path = source_path.with_suffix("")

    return _c_compile(source_path, output_path)


def c_run(raw_args=None):
    if raw_args is None:
        raw_args = sys.argv[1:]
    arg_parser = argparse.ArgumentParser(
        description="Compile and run C programs.",
        )
    arg_parser.add_argument(
        "file",
        type=Path,
        help="C source code path",
        )
    args, program_args = arg_parser.parse_known_args(raw_args)

    source_path = args.file.resolve()
    

    if not source_path.exists():
        print(f"ERROR: file {source_path} doesn't exist", file=sys.stderr)
        return 1
    
    output_path = source_path.with_suffix("")

    if (
            not output_path.exists()
            or os.path.getmtime(output_path) < os.path.getmtime(source_path)
        ):
        if (compiling_ret_code := _c_compile(source_path, output_path)) != 0:
            return compiling_ret_code
    else:
        print(f"INFO: skipping compilation")

    running_cmd = [
        str(output_path),
        *program_args,
        ]
    print(f"INFO: running {' '.join(running_cmd)}")
    running_proc = subprocess.run(running_cmd)

    return running_proc.returncode


if __name__ == "__main__":
    sys.exit(c_run())
