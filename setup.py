"""
Performs any neccessary setup before the main program is run
"""

import os
import os.path
import argparse
from shutil import copyfile

def main():

    file_path = os.listdir("music/")[0]


    # returns the file extension without the '.'
    file_type = os.path.splitext(file_path)[1][1:]
    file_path = os.path.join('music', file_path)
    copyfile(file_path, f"audio_data/complex.{file_type}")
    copyfile(file_path, f"audio_data/hfc.{file_type}")



if __name__ == "__main__":
    main()
