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


def validate_hashes(file1, file2):
    changed_files = []
    missing_files = []
    with open(file1, 'r') as f:
        hashes1 = json.load(f)
    with open(file2, 'r') as f:
        hashes2 = json.load(f)

    missing_files.append("{}:".format(file2))
    for file in hashes1:
        temp = hashes2.get(file, None)
        if temp is None:
            missing_files.append(file)
    missing_files.append("{}:".format(file1))
    for file in hashes2:
        temp = hashes1.get(file, None)
        if temp is None:
            missing_files.append(file)

    for file in hashes1:
        old = hashes1[file]
        new = hashes2.get(file, None)
        if new is not None and old != new:
            changed_files.append(file)
    return changed_files, missing_files


if sys.argv[1] == 'h':
    input_folder = sys.argv[2]
    output_file = sys.argv[3]
    hash_files_in_folder(input_folder, output_file)
elif sys.argv[1] == 'v':
    changed_result, missing_result = validate_hashes(sys.argv[2], sys.argv[3])
    with open("validator_changed_files.json", "w") as fil:
        json.dump(changed_result, fil)
    with open("validator_missing_files.json", "w") as fil:
        json.dump(missing_result, fil)
else:
    print("Unrecognized command, aborting")
