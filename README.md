# edge-computing
An edge computing project that is built on AWS IoT Greengrass to perform face recognition. 

# Components
- A script that runs on the client device that sends data and picks up the processed response.
- Client device attached to Greengrass core(EC2 instance)
- Greengrass component on the Greengrass core
- Lambda function for face-recognition(AWS Lambda)

# Design
This system involves a client device that simulates a camera that captures video data. The device sends these video frames using a script to the Greengrass component, which handles the face detection and sends the processed and encoded image data to an SQS queue. The AWS Lambda function has the queue enabled as the trigger, and this allows for the encoded data to be processed by the Lambda and sent back into another queue. The client script then picks up any updates to this response queue.
