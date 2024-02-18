<p align="center">
  <a href="https://play.google.com/store/apps/dev?id=7086930298279250852" target="_blank">
    <img alt="" src="https://github-production-user-asset-6210df.s3.amazonaws.com/125717930/246971879-8ce757c3-90dc-438d-807f-3f3d29ddc064.png" width=500/>
  </a>  
</p>

# 1. KBY-AI FaceSDK
## Overview
This project demonstrates an advanced `face recognition`, `face liveness-detection`, `face matching` technology implemented via pip install.

You can simple plug & play the above multi-functions from Python or from the command line with our KBY-AI pip library.

It also includes features that allow for testing face recognition, face anti-spoofing, face matching between two images using both image files and base64-encoded images.

  | Face Liveness Detection      | Face Recognition |
  |------------------|------------------|
  | Face Detection        | Face Detection    |
  | Face Liveness Detection        | Face Recognition    |
  | Pose Estimation        | Pose Estimation    |
  | 68 points Face Landmark Detection        | 68 points Face Landmark Detection    |
  | Face Quality Calculation        | Face Occlusion Detection        |
  | Face Occlusion Detection        | Face Occlusion Detection        |
  | Eye Closure Detection        | Eye Closure Detection       |
  | Mouth Opening Check        | Mouth Opening Check        |

## Features

#### Detect Face liveness in pictures

```python
from kbyai import facesdk
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read())
    return base64_data.decode("utf-8")

# Check liveness with a face image
filepath = "face.jpg"
result = facesdk.check_liveness(filepath)
print(result)

# Check liveness with an encoded face image data
file_base64 = image_to_base64(filepath)
result = facesdk.check_liveness_base64(file_base64)
print(result)
```

Find all the real & fake faces that appear in a picture:
![](https://github.com/kby-ai/IDCardRecognition-Docker/assets/153516004/532ff476-c86f-47fb-ae25-a4e887c2cab9)


#### Comparing faces with two different images

```python
from kbyai import facesdk
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read())
    return base64_data.decode("utf-8")

# Check similarity between two face images
filepath1 = "face1.jpg"
filepath2 = "face2.jpg"
result = facesdk.compare_face(filepath1, filepath2)
print(result)

# Check similarity between two encoded face images
file1_base64 = image_to_base64(filepath1)
file2_base64 = image_to_base64(filepath2)
result = facesdk.compare_face_base64(file1_base64, file2_base64)
print(result)
```

![](https://github.com/kby-ai/IDCardRecognition-Docker/assets/153516004/248915ba-cc16-4788-8f50-cee29c9b2f17)


If you want to run our library to do real-time face recognition on cross platforms, please check our product list here.

> [Face Liveness Detection - Android(Basic SDK)](https://github.com/kby-ai/FaceLivenessDetection-Android)
>
> [Face Liveness Detection - iOS(Basic SDK)](https://github.com/kby-ai/FaceLivenessDetection-iOS)
>
> [Face Recognition - Android(Standard SDK)](https://github.com/kby-ai/FaceRecognition-Android)
>
> [Face Recognition - iOS(Standard SDK)](https://github.com/kby-ai/FaceRecognition-iOS)
>
> [Face Recognition - Flutter(Standard SDK)](https://github.com/kby-ai/FaceRecognition-Flutter)
>
> [Face Recognition - React-Native(Standard SDK)](https://github.com/kby-ai/FaceRecognition-React-Native)
>
> [Face Attribute - Android(Premium SDK)](https://github.com/kby-ai/FaceAttribute-Android)
>
> [Face Attribute - iOS(Premium SDK)](https://github.com/kby-ai/FaceAttribute-iOS)


# 2. KBY-AI IDSDK
## Overview
This project demonstrates the server-based recognition capabilities for ID cards, passports, and driver's licenses.

At the core of this project lies the ID Card Recognition SDK, which has been developed to provide comprehensive support for recognizing ID cards, passports, and driver's licenses from over 180 countries.

You can simple plug & play the above function from Python or from the command line with our KBY-AI pip library.

#### ID document recognition with ID document image

![](https://github.com/kby-ai/IDCardRecognition-Docker/assets/153516004/a9bb9ef3-1c30-4dc3-9b5d-fdd34f4c975b)

```python
from kbyai import idsdk
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read())
    return base64_data.decode("utf-8")

# Check with ID card image file
filepath = "id.jpg"
result = idsdk.idcard_recognition(filepath)
print(result)

# Check with an encoded ID card Image data
file_base64 = image_to_base64(filepath)
result = idsdk.idcard_recognition_base64(file_base64)
print(result)

```

If you want to run our library to do real-time on cross platforms, please check our product list here.

> [IDCardRecognition-Docker](https://github.com/kby-ai/IDCardRecognition-Docker)
>
> [IDCardRecognition-Android](https://github.com/kby-ai/IDCardRecognition-Android)
>
> [IDCardRecognition-iOS](https://github.com/kby-ai/IDCardRecognition-iOS)
>
> [IDCardRecognition-Windows](https://github.com/kby-ai/IDCardRecognition-Windows)
>
> [IDCard-Recognition-SDK](https://github.com/kby-ai/IDCard-Recognition-SDK)
>

## Online Demos
  You can test the SDK using images from the following URL:
  https://web.kby-ai.com



# 3. Our Product List

👏  We have published the Face Liveness Detection, Face Recognition SDK and ID Card Recognition SDK.

https://github.com/kby-ai/Product

# 4. Contact US


Email: contact@kby-ai.com

Telegram: @kbyai

WhatsApp: +19092802609

Skype: live:.cid.66e2522354b1049b

Facebook: https://www.facebook.com/KBYAI