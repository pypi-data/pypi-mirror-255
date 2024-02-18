"""
#
# Shortcut collections
#
# Copyright(c) 2018, Carium, Inc. All rights reserved.
#
"""

import hashlib
import io
import uuid
from importlib import import_module


def import_class(class_fullname: str):
    """Importing a class from full-representative class name"""
    modname, clsname = class_fullname.rsplit(".", 1)
    return getattr(import_module(modname), clsname)


def get_file_sha(file: io.IOBase) -> str:
    """Return SHA512 of a file"""
    m = hashlib.sha512()
    file.seek(0)
    for line in file:
        if hasattr(line, "encode"):  # Convert to bytes if necessary
            line = line.encode()  # pyre-ignore[16]
        m.update(line)

    return m.hexdigest()


def uuid_hex(_id: str) -> str:
    """Get the hex-version of a UUID"""
    return uuid.UUID(_id).hex
