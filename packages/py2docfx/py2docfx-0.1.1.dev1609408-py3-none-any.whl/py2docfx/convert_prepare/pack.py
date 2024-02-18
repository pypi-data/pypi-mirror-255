import shutil
from os import path
from zipfile import ZipFile
import os
import wheel.cli.unpack as wheel_cli_unpack


def unpack_dist(dist_file):
    if dist_file.endswith(".whl"):
        unpack_wheel(dist_file)
    else:
        unpack_compressed(dist_file)

def unpack_compressed(file_path):
    """
    Transform a tar.gz/zip file to a folder containing source code
    """

    shutil.unpack_archive(file_path, path.dirname(file_path))


def unpack_wheel(file_path):
    """
    Transform a wheel file to a folder containing source code
    """

    wheel_cli_unpack.unpack(file_path, path.dirname(file_path))
    extract_folder = [file for file in os.listdir(path.dirname(file_path)) if path.isdir(path.join(path.dirname(file_path), file))][0]
    data_folder = path.join(path.dirname(file_path), extract_folder, extract_folder + ".data")
    if path.exists(data_folder):
        for subfolder in ["purelib", "platlib"]:
            if path.exists(path.join(data_folder, subfolder)):
                for file in os.listdir(path.join(data_folder, subfolder)):
                    shutil.move(path.join(data_folder, subfolder, file), path.join(path.dirname(file_path), extract_folder))
        shutil.rmtree(data_folder)
