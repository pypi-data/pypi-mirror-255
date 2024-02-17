import os
from enum import Enum


class DirItemPolicy(Enum):
    FilesAndDirs = 1  # files first, then dirs (each group in alphabetic order)
    DirsAndFiles = 2  # dirs first, then files (each group in alphabetic order)
    AllAlphabetic = 3  # file and dirs together, in alphabetic order
    OnlyFilesAlphabetic = 4  # only files, in alphabetic order
    OnlyDirsAlphabetic = 5  # only dirs, in alphabetic order


def dirItems(path, files=DirItemPolicy.FilesAndDirs, fromDepth=0, maxDepth=65535):
    if maxDepth < 0:
        return []
    # the items that will be returned by the function
    items = []
    # items that are files (temporarily stored here for proper ordering)
    fileItems = []
    # items that are directories (temporarily stored here for proper ordering and for recursive calls)
    directoryItems = []
    for item in os.listdir(path):
        itemPath = os.path.join(path, item)
        if os.path.isfile(itemPath) and fromDepth <= 0:
            if files == DirItemPolicy.FilesAndDirs or files == DirItemPolicy.DirsAndFiles:
                fileItems.append(itemPath)
            elif files == DirItemPolicy.AllAlphabetic or files == DirItemPolicy.OnlyFilesAlphabetic:
                items.append(itemPath)
        elif os.path.isdir(itemPath):
            directoryItems.append(itemPath)
            if files == DirItemPolicy.AllAlphabetic or files == DirItemPolicy.OnlyDirsAlphabetic:
                if fromDepth <= 0:
                    items.append(itemPath)

    # generate final list
    if fromDepth <= 0:
        if files == DirItemPolicy.FilesAndDirs:
            items = fileItems + directoryItems
        elif files == DirItemPolicy.DirsAndFiles:
            items = directoryItems + fileItems

    # recursive calls
    for directory in directoryItems:
        items += dirItems(directory, files, fromDepth - 1, maxDepth - 1)

    return items
