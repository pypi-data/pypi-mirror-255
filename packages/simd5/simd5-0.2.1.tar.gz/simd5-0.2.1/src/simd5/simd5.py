#!/usr/bin/env python3
#
# Python module to create MD5 files that contains the
#   MD5 hash of all the files in a subdirectory for digital deliveries.
# v 0.2.1
# 
# 06 Feb 2024
#
# Digitization Program Office,
# Office of the Chief Information Officer,
# Smithsonian Institution
# https://dpo.si.edu
#
# 
# Import modules
import os
import glob

# from pathlib import Path
from time import localtime, strftime

# Parallel
import multiprocessing
from p_tqdm import p_map


def md5sum(filename):
    """
    Get MD5 hash from a file.
    """
    # https://stackoverflow.com/a/7829658
    import hashlib
    from functools import partial
    # Open file and calculate md5 hash
    with open("{}".format(filename), mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    # Return filename and md5 hash
    return filename, d.hexdigest()


def md5_file(folder=None, fileformat="m f", workers=multiprocessing.cpu_count(), forced=False):
    # If there is already a md5 file, ignore unless forced is True
    if len(glob.glob("{}/*.md5".format(folder))) > 0 and forced is False:
        print("\n   md5 file exists, skipping...")
        return
    # Scan the folder
    list_folder = os.scandir(folder)
    files = []
    for entry in list_folder:
        # Only get files, ignore folders
        if entry.is_file():
            files.append("{}/{}".format(folder, entry.name))
    if len(files) == 0:
        print("\n There are no files in {}".format(folder))
        return
    else:
        print("\n Running on {} using {} workers".format(folder, workers))
        # Calculate md5 hashes in parallel using a progress bar
        results = p_map(md5sum, files, **{"num_cpus": int(workers)})
        with open("{}/{}_{}.md5".format(folder, os.path.basename(folder), strftime("%Y%m%d%H%M%S", localtime())),
                  'w') as fp:
            for res in results:
                # Save according to the format selected
                if fileformat == "m f":
                    fp.write("{} {}\n".format(res[1], os.path.basename(res[0])))
                elif fileformat == "f m":
                    fp.write("{} {}\n".format(os.path.basename(res[0]), res[1]))
                elif fileformat == "m,f":
                    fp.write("{},{}\n".format(res[1], os.path.basename(res[0])))
                elif fileformat == "f,m":
                    fp.write("{},{}\n".format(os.path.basename(res[0]), res[1]))
        return
