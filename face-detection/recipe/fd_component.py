#!/usr/bin/env python3
import sys
import os
import json
import base64
import boto3
import time
from awscrt import io, mqtt, auth
from awsiot import mqtt_connection_builder

THIS_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(THIS_DIR, "face_detection"))
from face_detection import FaceDetection

print("FaceDetection starting up…", flush=True)

# if len(sys.argv) != 3:
#     sys.exit(1)

sqs = boto3.client("sqs", region_name="us-east-1")
TOPIC = "clients/1232034091-IoTThing"
QUEUE_URL = f"https://sqs.us-east-1.amazonaws.com/396608811399/1232034091-req-queue"
RESPONSE_URL = f"https://sqs.us-east-1.amazonaws.com/396608811399/1232034091-resp-queue"

ENDPOINT = "a11hd8wezkkpi7-ats.iot.us-east-1.amazonaws.com"

CERT = "/greengrass/v2/certs/device.pem.crt"
KEY  = "/greengrass/v2/certs/privkey.pem.key"
CA   = "/greengrass/v2/certs/AmazonRootCA1.pem"

mqtt_conn = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    port=8883,
    cert_filepath=CERT,
    pri_key_filepath=KEY,
    ca_filepath=CA,
    client_id="FaceDetectionComponent",
    clean_session=False,
    keep_alive_secs=30
)


mqtt_conn.connect().result()

detector = FaceDetection()

def on_mqtt_message(topic, payload, **_):
    print(f"Callback triggered! topic={topic!r}, payload={payload[:50]!r}…", flush=True)
    try:
        msg = json.loads(payload.decode("utf-8"))
        rid = msg.get("request_id")
        content = msg.get("encoded") or msg.get("content")
        fname = msg.get("filename")
        if not (rid and content and fname):
            return
        raw = base64.b64decode(content)
        os.makedirs("/tmp/input", exist_ok=True)
        in_path = f"/tmp/input/{os.path.basename(fname)}"
        with open(in_path, "wb") as f:
            f.write(raw)
        out_path = detector.detect(in_path, "/tmp/output")
        if out_path:
            with open(out_path, "rb") as f:
                face_b64 = base64.b64encode(f.read()).decode("utf-8")
            body = {"request_id": rid, "face_img": face_b64}
            os.remove(out_path)
            sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(body))
        else:
            body = {"request_id": rid, "result": "No-Face"}
            sqs.send_message(QueueUrl=RESPONSE_URL, MessageBody=json.dumps(body))
        print("Something is hopefully happening")

    except Exception as e:
        print("Error comes here", e)
    finally:
        try:
            os.remove(in_path)
        except:
            pass

print("MQTT connected, now subscribing...", flush=True)

try:
    subscribe_future, packet_id = mqtt_conn.subscribe(
        topic=TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_mqtt_message
    )
    subscribe_future.result()
    print(f"Subscribed to {TOPIC!r} (packet id {packet_id})", flush=True)     

except Exception as e:
    print(f"Subscription failed for topic {TOPIC!r}: {e!r}", flush=True)      


while True:
    time.sleep(60)

