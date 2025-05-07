# Edge Computing
An edge computing project that is built on AWS IoT Greengrass to perform face recognition. 

# Components
- A script that runs on the client device that sends data and picks up the processed response.
- Client device attached to Greengrass core(EC2 instance)
- Greengrass component on the Greengrass core
- Lambda function for face-recognition(AWS Lambda)

# Design
This system involves a client device that simulates a camera that captures video data. The device sends these video frames using a script to the Greengrass component, which handles the face detection and sends the processed and encoded image data to an SQS queue. The AWS Lambda function has the queue enabled as the trigger, and this allows for the encoded data to be processed by the Lambda and sent back into another queue. The client script then picks up any updates to this response queue.

# Explanation
- artifact folder - This folder consists of all of the business logic of our current system.
  - The face detection logic
  - The logic that handles the subsciption and publishing of messages using MQTT.
  - The logic that posts to the queue using the processed information from the face detection code.
 
- recipe folder - This folder consists of the configuration that spins up our python processes mentioned in the artifact folder.

- script - [link](https://github.com/CSE546-Cloud-Computing/CSE546-SPRING-2025/tree/project-2-part-2)
