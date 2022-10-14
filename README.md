# Making Vehicles Transparent via V2V Vedio Streaming

### Graduation Project 2022-2023 supported by Valeo co. mentorship program

### This Project is  a 3-phase project implementation

### under supervision of Prof. Khaled El-Shafie

# System Design and Architecture

![image](https://user-images.githubusercontent.com/58345649/195928204-40d590f2-13e9-4dcd-8814-abf916c0943b.png)

## Our Project architecture mainly divided into subsystems:

### Cameras And Sensors Subsystem:
> To scan and take the live event in front of the vehicle.
> Sensors is to detect the actual distances needed.

### Vision System:
>  To verify the data from Camera and Sensors.

### CPU:
> To apply the logic of transparency using AI and Computer Vision models.
> To do all mathematical calculations for distance.
> Manage All Subsystems.
> Send data to Communication subsystem to be sent to another vehicle.

### Communication Subsystem:
> Communicate and interact with other vehicles via Wifi technology.
Consists of :
> Wifi for Sending.
> Wifi for receiving.
> Gateway/Access point module to connect this vehicle to other vehicles. 

# Project Development Phases

## Phase_1: Establishing all basic features.
> Communication.
> Streaming data in coordinates format.
> Distance Mathematical Operations.
> Computer Vision Model.

## Phase_2:
> Upgrade data Transmission to Video stream.
> Enhance Computer Vision and ML models to increase accuracy.
> Initiate ML model to detect the percentage of successful passing.
> Initiate Triple Modular Redundancy and Voter Module for Verification Inputs.

## Phase_3:
> Additional features:
> Create Server For IOT and Traffic management Features.
> IOT: Find my Vehicle service.
> Traffic management: create a ML model to monitor and suggest better road path.

# System Scenarios

> This project aims to create a cooperative driver-assistance system for the passing of vision-obstructing vehicles, which combines several technologies to save the passing drivers’ life from unpredictable vehicle moving in the same direction even opposite direction.
> Once there are a car need to pass a vision-obstructing vehicle but the driver of the rear vehicle doesn’t see what is in front of that vision-obstructing vehicle just enabling this system that scenario will occurred.

> In Vehicle_1 (vision-obstructing):
>> It normally scans objects in vehicle type and detect its coordinates (3 road lines at most: direct front, front right, front left) using Camera and Sensors and Computer Vision model and make some mathematical equations to get the most accurate distances, it will be kept for future propose.

> In Main Vehicle (Normal User):
>>Camera takes a photo of the vehicle_1 (photo contains the vehicle data “No, ID”).
Using an encryption method the SSID, Password of the vehicle_1 will be generated (This technique doesn’t Need for internet connection), Then this vehicle will connect to the vehicle_1’s Access point using the receiving Wifi.
As soon as connection is stablished the data transfer will be occurred.

>> Date consists of:
The Front vehicle Data (Length , Height).
Coordinates of the vehicle in front of vehicle_1).

