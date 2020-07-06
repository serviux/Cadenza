
import boto3
import argparse
import os, os.path
from shutil import copyfile
from music_data import MusicData
from db_util import create_connect_table

s3 = boto3.resource("s3")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
bucket = s3.Bucket("joshcormiercadenza")





def upload_files_s3(filepath):
    filename = os.path.split(filepath)[-1:][0].replace(" ", "_")
    name_no_ext, ext = os.path.splitext(filename)
    bucket.upload_file(filepath, f"{name_no_ext}/{filename}")
    bucket.upload_file("audio_data/complex.png", f"{name_no_ext}/diagrams/complex.png")
    bucket.upload_file("audio_data/hfc.png", f"{name_no_ext}/diagrams/hfc.png")
    bucket.upload_file("audio_data/beats.png", f"{name_no_ext}/diagrams/beats.png")
    bucket.upload_file(f"audio_data/complex{ext}", 
                        f"{name_no_ext}/audio/complex{ext}")
    bucket.upload_file(f"audio_data/hfc{ext}",
                        f"{name_no_ext}/audio/hfc{ext}")
    

def save_to_dynamodb(music_data):
    """Takes the processing data from the MusicData class
    and uploads it to dynamodb
    Parameters
    ----------
    music_data: MusicData
        class containing info about a music"""
    table = create_connect_table()
    table.put_item(Item=music_data.to_dict())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", "--file-path", help="Path to the audio file")
    parser.add_argument("-a", "--artist", help="Name of the artist of the song")
    parser.add_argument("-t", "--title", help="title of the song")

    args = parser.parse_args()
    if args.file_path is None or not os.path.exists(args.file_path):
        print("invalid file path")
        return
    if args.artist is None:
        print("no artist provided")
        return
    if args.title is None:
        print("no title provided")
        return

    md = MusicData(args.file_path, title=args.title, artist=args.artist)
    md.detect_beats()
    md.detect_onsets()
    md.save_beat_diagram()
    md.save_onsets_diagram()
    upload_files_s3(args.file_path)
    save_to_dynamodb(md)




if __name__ == '__main__':
    main()