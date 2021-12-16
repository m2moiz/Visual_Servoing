# Visual Servoing Project

This repository contains the code for the final project of the visual servoing course

## Problem Statement

A camera is mounted onto the ceiling using which we can view the workspace below. We want to move the robot using only the camera feed as the sensory input. 

### Objectives

Concretely we can define the objectives as:

 1. Get the current pose (Rotation and Orientation) of the Robot (Turtlebot3).
2. Make the Robot move to an arbitrary position in the workspace specified by the user.
 3. Make the robot avoid obstacles placed in the enviroment, whle moving to the goal position.

## Software Setup

 - **Ubuntu Version**:  *[Ubuntu 20.04](https://releases.ubuntu.com/20.04/)*
 - **Ros Version**: *[Ros Noetic](http://wiki.ros.org/noetic/Installation)*
 - **Python Version**: *[Python 3 (Anaconda)](https://www.anaconda.com/products/individual)*
 - **OpenCV Version**: [*OpenCV 4.5.4*](https://anaconda.org/conda-forge/opencv)


## Functionality Development Pipeline Overview
![VS_Pipeline drawio](https://user-images.githubusercontent.com/5123355/146275950-0703131e-bdec-46f6-b064-a56a3f7b3044.png)

## Camera Calibration

## Estimating the Pose

### ArUco Markers
ArUco markers are binary square fiducial markers that can be used for camera pose estimation. Their main benefit is that their detection is robust, fast and simple. The aruco module includes the detection of these types of markers and the tools to employ them for pose estimation and camera calibration.

To extract the pose from the ArUco marker we use the [OpenCV ArUco Module](https://docs.opencv.org/4.x/d9/d6d/tutorial_table_of_content_aruco.html). While it is easy to create aruco markers using OpenCV, we used this [tool](https://chev.me/arucogen/) to download and print out markers. 

For our use case we have mounted the markers on top of the robot as seen in the image below.

![aruco marker](https://user-images.githubusercontent.com/5123355/146277689-d46df22b-6072-493c-b801-f9aaa6bad0de.png)

### Estimating the Current Pose
Current Pose refers to the position and orientation of the robot within the current image frame. As the robot moves around it makes sence that its pose will change. 
<p align="center">
  <img src="https://user-images.githubusercontent.com/5123355/146279445-2105ee1c-8795-4d21-b2c3-9f2a899e8feb.png" width="45%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="Dark" src="https://user-images.githubusercontent.com/5123355/146279455-7075e515-52fa-435e-a8cc-e6027d9ff34d.jpg" width="45%">
</p>


The image on the left represents the image frame received from the camera while the image on the right shows the same frame with the detected pose being shown on top. The image frame above corresponds to the robots starting position in the workspace.

#### Running the code:

To perform pose detection on a simulated enviroment, use the command

    roslaunch vs_project pose_estimation.launch mode:="sim"

To perform pose detection on the real robot, use the command

    roslaunch vs_project pose_estimation.launch mode:="real"

### Estimating the Goal Pose
There are two approaches we can take to estimate the pose of the robot. The first one is to place a second marker in the goal position and extract the pose from it.
The second approach is to place the robot in the goal position and take a picture from the camera. Using that picture we can extract the pose of the robot when it is in the goal position. 
We use the second approach here, in our implementation.

<p align="center">
  <img src="https://user-images.githubusercontent.com/5123355/146283083-2b9550cb-c3d0-4a23-b4e4-5c55bd9538ac.png" width="45%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="Dark" src="https://user-images.githubusercontent.com/5123355/146283092-784f4a6b-e856-4e5c-9be0-70b6386f8934.jpg" width="45%">
</p>

The image on the left represents the image taken with the robot at the goal position, while the one on the right is the same image but with the pose detection run on it.

#### Running the code:

To get the estimated goal pose, we run the following command

    roslaunch vs_project goal_pose_estimation.launch

One thing to be careful of while running this launch file is the path of the image. 
In line **4** of the `goal_pose_estimation.launch`file is where we specify the path i.e `<arg name="image" default="$(find vs_project)/parking2.png"/>` 

## Controller Implementation

## Occupancy Grid Generation

## Path Planning







