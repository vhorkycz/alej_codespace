#!/usr/bin/env python3

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys


ALLOWED_TYPES = {"int", "long", "char", "str"}


def parse_type_var(raw: str) -> tuple[str, str]:
    if ":" not in raw:
        raise ValueError(f"missing `:` between type and variable name in {raw!r}")
    type_, var = raw.split(":", maxsplit=1)
    if not type_.strip():
        raise ValueError(f"missing type in {raw!r}")
    if type_ not in ALLOWED_TYPES:
        raise ValueError(
            f"unknown type `{type_}`, possible types are: "
            + ", ".join(f"`{t}`" for t in sorted(ALLOWED_TYPES))
            )
    if not var.strip():
        raise ValueError(f"missing variable name in {raw!r}")
    return (type_, var)


def _make_c_template(
        params: Sequence[tuple[str, str]],
        include_stdbool: bool = True,
        include_stdio: bool = True,
        typedef_str: bool = True,
    ):
    lines = []
    
    if include_stdbool:
        lines.append("#include <stdbool.h>")
    if include_stdio:
        lines.append("#include <stdio.h>")
    if any(type_ in ["int", "long"] for type_, __ in params):
        lines.append("#include <stdlib.h>")

    if typedef_str:
        str_type = "str "
        if lines:
            lines.append("")
        lines.append("typedef char *str;")
    else:
        str_type = "char *"

    if lines:
        lines.append("")

    main_body = []
    if params:
        main_params = f"int argc, {str_type}argv[]"
        for i, (type_, var_name) in enumerate(params, start=1):
            if type_ in ["int", "long"]:
                arg_var = f"{type_} {var_name} = ato{type_[0]}(argv[{i}]);"
            elif type_ == "char":
                arg_var = f"{type_} {var_name} = argv[{i}][0];"
            elif type_ == "str":
                arg_var = f"{str_type}{var_name} = argv[{i}];"
            else:
                raise ValueError(f"unknown type {type_}")
            main_body.append(arg_var)
    else:
        main_params = "void"

    if main_body:
        main_body.append("")
    main_body.extend([
        "/*",
        "",
        "sem doplnte svuj kod",
        "",
        "*/",
        "",
        "return 0;",
        ])
                      
    lines.append(f"int main({main_params}) {{")
    lines.extend(" " * 4 + line for line in main_body)
    lines.extend("}")

    return "\n".join(lines)


def make_c_template(args=None):
    if args is None:
        args = sys.argv[1:]
    arg_parser = argparse.ArgumentParser(
        description="Make C source code templates."
        )
    arg_parser.add_argument(
        "arg",
        nargs="*",
        help=(
            "`<type>:<variable_name>`, type can be any of: "
            + ", ".join(f"`{t}`" for t in sorted(ALLOWED_TYPES))
            ),
        )
    arg_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="output file",
        )
    arg_parser.add_argument(
        "--no-stdio",
        action="store_true",
        help="don't include `stdio.h`",
        )
    arg_parser.add_argument(
        "--no-stdbool",
        action="store_true",
        help="don't include `stdbool.h`",
        )
    arg_parser.add_argument(
        "--no-str",
        action="store_true",
        help="don't include `str` alias for `char *`",
        )                    

    args = arg_parser.parse_args(args)
    types_vars = []
    types_vars_ok = True
    for raw_type_var in args.arg:
        try:
            type_var = parse_type_var(raw_type_var)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            types_vars_ok = False
        else:
            types_vars.append(type_var)
    if not types_vars_ok:
        return 1

    template = _make_c_template(
        types_vars,
        include_stdbool=not args.no_stdbool,
        include_stdio=not args.no_stdio,
        typedef_str=not args.no_str,
        )
    if out_path := args.output:
        with open(out_path, mode="w") as out_file:
            print(template, file=out_file)
    else:
        print(template)
    return 0
        
if __name__ == "__main__":
    sys.exit(make_c_template())
