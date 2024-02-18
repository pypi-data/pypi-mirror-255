import requests
import argparse

def check_liveness(filepath):

    url = "http://45.14.49.42:8085/check_liveness"

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


def check_liveness_base64(base64_data):

    url = "http://45.14.49.42:8085/check_liveness_base64"

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


def compare_face(filepath1, filepath2):

    url = "http://45.14.49.42:8081/compare_face"

    try:
        with open(filepath1, 'rb') as file1, open(filepath2, 'rb') as file2:
            files = {'file1': file1, 'file2':file2}

            response = requests.post(url, files=files)
            if response.status_code == 200:
                print("Successfully connected KBY-AI Server!")
                print("Response content: ", response.json())
            else:
                print("Error Response: ", response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

def compare_face_base64(base64_data1, base64_data2):

    url = "http://45.14.49.42:8081/compare_face_base64"

    try:
        data = {'base64_1': base64_data1, 'base64_2':base64_data2}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Successfully connected KBY-AI Server!")
            print("Response content: ", response.json())
        else:
            print("Error Response: ", response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="KBY-AI LIMITED SDK CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: check_liveness
    check_liveness_parser = subparsers.add_parser("check_liveness", help="Description : Check liveness of a face image")
    check_liveness_parser.add_argument("filepath", help="Path to the face image file")

    # Command: check_liveness_base64
    check_liveness_base64_parser = subparsers.add_parser("check_liveness_base64", help="Description : Check liveness of an encoded face image")
    check_liveness_base64_parser.add_argument("base64_data", help="Path to the face image file")

    # Command: compare_face
    compare_face_parser = subparsers.add_parser("compare_face", help="Description : Compare two face images")
    compare_face_parser.add_argument("filepath1", help="Path to the 1st face image file")
    compare_face_parser.add_argument("filepath2", help="Path to the 2nd face image file")

    # Command: compare_face_base64
    compare_face_base64_parser = subparsers.add_parser("compare_face_base64", help="Description : Compare two encoded face images")
    compare_face_base64_parser.add_argument("base64_data1", help="Path to the 1st face image file")
    compare_face_base64_parser.add_argument("base64_data2", help="Path to the 2nd face image file")

    args = parser.parse_args()

    if args.command == "check_liveness":
        check_liveness(args.filepath)
    elif args.command == "check_liveness_base64":
        check_liveness_base64(args.base64_data)
    elif args.command == "compare_face":
        compare_face(args.filepath1, args.filepath2)
    elif args.command == "compare_face_base64":
        compare_face_base64(args.base64_data1, args.base64_data2)
    else:
        print("Invalid command. Use 'facesdk.py -h' for help.")
