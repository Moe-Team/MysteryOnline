import hashlib
import sys
import os
import json


BLOCKSIZE = 65536


def hash_file(filename):
    hasher = hashlib.sha1()
    with open(filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


def hash_files_in_folder(folder, json_file):
    hashed_files = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_filename = os.path.join(root, file)
            print("Hashing {}".format(full_filename))
            result = hash_file(full_filename)
            hashed_files[full_filename] = result
    print("Done, dumping to {}".format(json_file))
    with open(json_file, 'w') as f:
        json.dump(hashed_files, f)


input_folder = sys.argv[1]
output_file = sys.argv[2]
hash_files_in_folder(input_folder, output_file)
