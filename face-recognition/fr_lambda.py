import json
import boto3
import os
import base64
from face_recognition.lamda_function import face_recognition 

def lambda_handler(event, context):
    record = event["Records"][0]
    raw_body = record.get("body")

    body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

    request_id = body.get("request_id")
    face_img = body.get("face_img")
    model_wt_path = "resnetV1_video_weights.pt"
    model_path = "resnetV1.pt"

    recognizer = face_recognition()

    os.makedirs("/tmp/input", exist_ok=True)
    face_img_path = os.path.join("/tmp/input", f"{request_id}_face.jpg")
    with open(face_img_path, "wb") as f:
        f.write(base64.b64decode(face_img)) 

    result = recognizer.face_recognition_func(model_path, model_wt_path, face_img_path)
    sqs = boto3.client('sqs', region_name='us-east-1')
    queue_url = "https://sqs.us-east-1.amazonaws.com/396608811399/1232034091-resp-queue"
    message_body = json.dumps({
        "request_id": request_id,
        "result": result
    })

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )
    
    return {
        "statusCode": 200,
        "body": message_body
    }
