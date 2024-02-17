import hashlib

from src.io.ioUtils import DirItemPolicy, dirItems

bufferSize = 65536

def digestHexFilesInPath(path, fromDepth=0, maxDepth=65535):
    hash = hashlib.sha256()
    files = dirItems(path, DirItemPolicy.OnlyFilesAlphabetic, fromDepth, maxDepth)
    for file in files:
        with open(file, 'rb') as f:
            while True:
                data = f.read(bufferSize)
                if not data:
                    break
                hash.update(data)
    return hash.hexdigest()


