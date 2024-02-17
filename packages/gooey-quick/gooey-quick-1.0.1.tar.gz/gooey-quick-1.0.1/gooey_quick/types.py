import os
from typing import NewType, TypeVar, Generic
from pathlib import Path, PurePath, PureWindowsPath, PurePosixPath

T = TypeVar('T')


class FileWithExtension(PurePath, Generic[T]):
    """
    A generic Path that takes a Literal of file's allowed extensions.
    This basically exists so as to allow gooey_quick user to set the
    wildcard option on the File and Folder choosers widgets. See:
    https://github.com/chriskiehl/Gooey/blob/master/docs/Gooey-Options.md#file-and-folder-choosers
    and examples/filetypes_gooey_quick.py
    """
    def __new__(cls, *args):
        if cls is FileWithExtension:
            cls = PureWindowsPath if os.name == 'nt' else PurePosixPath
        self = cls._from_parts(args)
        return self


DirectoryPath = NewType('DirectoryPath', Path)

SaveToPath = NewType('SaveToPath', Path)

