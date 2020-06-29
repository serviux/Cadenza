
import boto3
import argparse
import os, os.path
from shutil import copyfile
from music_data_handler import MusicData

s3 = boto3.resource("s3")
dynamodb = boto3.resource("dyanamodb")
bucket = s3.Bucket("joshcormiercadenza")



def create_connect_table():
    """tries to connect to the table or create the table"""
    table = None
    try:
        table = dynamodb.Table("music_data")
        table.rowcount()
        return table
    except Exception:
        table = dynamodb.create_table(
            TableName='music_data',
            KeySchema=[
                {
                    'AttributeName': "title",
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': "title",
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'title',
                    'AttributeType': 'S',
                },
                {
                    'AttributeName': 'artist',
                    'AttributeType': 'S',
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }

        )
        table.meta.client.get_waiter('table_exists').wait(TableName='music_data')
        return table

def copy_to_audio_folder(file_path):
    """Copies the song to the audio/ subdirectory
    
    Parameters
    ----------
    file_path: String
        file to be copied to audio/complex.mp3 and audio/hfc.mp3"""
    if not os.path.exists("audio_data"):
        os.mkdir("audio_data")
    copyfile(file_path, "audio_data/complex.mp3")
    copyfile(file_path, "audio_data/hfc.mp3")
    


def upload_files_s3(filepath):
    filename = os.path.split(filepath)[-1:][0].replace(" ", "_")
    name_no_ext, _ = os.path.splitext(filename)
    bucket.upload_file(filepath, f"{name_no_ext}/{filename}")
    bucket.upload_file("audio_data/complex.png", f"{name_no_ext}/diagrams/complex.png")
    bucket.upload_file("audio_data/hfc.png", f"{name_no_ext}/diagrams/hfc.png")
    bucket.upload_file("audio_data/beats.png", f"{name_no_ext}/diagrams/beats.png")


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
    if args.title is None:
        print("no title provided")

    copy_to_audio_folder(args.file_path)
    md = MusicData(args.file_path, title=args.title, artist=args.title)
    md.detect_beats()
    md.detect_onsets()
    md_data = md.json()
    md.save_beat_diagram()
    md.save_onsets_diagram()
    upload_files_s3(args.file_path)





if __name__ == 'main':
    main()