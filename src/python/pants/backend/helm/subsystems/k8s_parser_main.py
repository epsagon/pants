# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import sys

from hikaru import load_full_yaml


def main(args: list[str]):
    input_filename = args[0]

    found_image_refs: dict[tuple[int, str], str] = {}

    with open(input_filename, "r") as file:
        try:
            parsed_docs = load_full_yaml(stream=file)
        except RuntimeError:
            # Hikaru fails with a `RuntimeError` when it finds a K8S manifest for an
            # API version and kind that doesn't understand.
            #
            # We use this exit code to notify the Pants rule that this file needs to be ignored.
            sys.exit(2)

    for idx, doc in enumerate(parsed_docs):
        entries = doc.find_by_name("image")
        for entry in entries:
            entry_value = doc.object_at_path(entry.path)
            entry_path = "/".join(map(str, entry.path))
            found_image_refs[(idx, entry_path)] = str(entry_value)

    for (idx, path), value in found_image_refs.items():
        print(f"{idx},/{path},{value}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Missing file argument", file=sys.stderr)
        print(f"Syntax: {sys.argv[0]} <file>", file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1:])
