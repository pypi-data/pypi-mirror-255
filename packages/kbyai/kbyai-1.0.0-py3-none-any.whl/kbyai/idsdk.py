import requests
import argparse

def idcard_recognition(filepath):

    url = "http://45.14.49.42:8082/idcard_recognition"

    file = {'file': open(filepath, 'rb')} 

    try:
        response = requests.post(url, files=file)    
        if response.status_code == 200:
            print("Successfully connected KBY-AI Server!")
            print("Response content: ", response.json())
        else:
            print("Error Response: ", response.text)
    finally:
        file['file'].close()

def idcard_recognition_base64(base64_data):

    url = "http://45.14.49.42:8082/idcard_recognition_base64"

    # Create a dictionary with the base64 data
    data = {
        'base64': base64_data
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Successfully connected KBY-AI Server!")
        print("Response content: ", response.json())
    else:
        print("Error Response: ", response.text)

def main():
    parser = argparse.ArgumentParser(description="KBY-AI LIMITED SDK CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: idcard_recognition
    idcard_recognition_parser = subparsers.add_parser("idcard_recognition", help="Description : ID Card Recognition from Input ID image")
    idcard_recognition_parser.add_argument("filepath", help="Path to the face image file")

    # Command: idcard_recognition_base64
    idcard_recognition_base64_parser = subparsers.add_parser("idcard_recognition_base64", help="Description : ID Card Recognition from encoded ID image data")
    idcard_recognition_base64_parser.add_argument("base64_data", help="Path to the face image file")

    args = parser.parse_args()

    if args.command == "idcard_recognition":
        idcard_recognition(args.filepath)
    elif args.command == "idcard_recognition_base64":
        idcard_recognition_base64(args.base64_data)
    else:
        print("Invalid command. Use 'idsdk.py -h' for help.")
