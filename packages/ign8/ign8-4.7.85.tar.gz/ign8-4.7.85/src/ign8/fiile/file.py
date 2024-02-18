import os

def follow(initial_symlink):
    while os.path.islink(initial_symlink):
        target = os.readlink(initial_symlink)
        initial_symlink = target
    return initial_symlink