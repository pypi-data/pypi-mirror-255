import os
import re
import glob
import shutil
from pathlib import Path


def make_dir(wdir):
    if not os.path.isdir(wdir):
        os.makedirs(wdir)


def check_dir(path):
    wdir = os.path.dirname(path)
    if os.path.isdir(wdir):
        return True
    return False


def check_file(path):
    if os.path.isfile(path):
        return True
    return False


def rename_dir(src, dst):
    if not os.path.isdir(src):
        os.rename(src, dst)
    else:
        os.makedirs(dst)


def copy_file(src, dst):
    shutil.copy(src, dst)


def copy_dir(src, dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def remove_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def remove_file(path):
    os.remove(path)


# rename files using regular expressions
# see: https://docs.python.org/2/library/re.html
# example: rename_files(sdir, '*.png', r'^(.*)_KRO(.*)\.png$', r'sim_KRO\2.png')
#          \1 argument will be replaced by sim_, \2 argument will be kept unchanged
def rename_files(sdir, files, pattern, replacement, only_check=False, verbose=False):
    for pathname in glob.iglob(os.path.join(sdir, files)):
        basename = os.path.basename(pathname)
        newname = re.sub(pattern, replacement, basename)
        if verbose and only_check:
            print(newname)
        elif newname != basename:
            os.rename(pathname, os.path.join(sdir, newname))


# rename directories using regular expressions
# see: https://docs.python.org/2/library/re.html
# example: rename_dirs( sdir, r'^(.*)_KRO(.*)$', r'sim_KRO\2' )
#          \1 argument will be replaced by sim_, \2 argument will be kept unchanged
def rename_dirs(sdir, pattern, replacement, only_check=False, verbose=False):
    for basename in os.listdir(sdir):
        newname = re.sub(pattern, replacement, basename)
        if verbose and only_check:
            print(newname)
        elif newname != basename:
            os.rename(os.path.join(sdir, basename), os.path.join(sdir, newname))


# get file name
def get_filename(file):
    return Path(file).stem
