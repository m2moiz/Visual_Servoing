# Visual Servoing Project

This repository contains the code for the final project of the visual servoing course

https://user-images.githubusercontent.com/5123355/146294092-ef9497d3-2b20-4d84-a10a-c19e97768b6d.mp4



https://user-images.githubusercontent.com/5123355/146295816-8162ddf2-aa26-4538-8beb-2ee574596611.mp4



https://user-images.githubusercontent.com/5123355/146295831-fde5bfc9-c9b4-4586-93d9-c842f1041bcd.mp4



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
Camera calibration is the process of estimating intrinsic and/or extrinsic parameters. Intrinsic parameters deal with the camera's internal characteristics, such as, its focal length, skew, distortion, and image center. Extrinsic parameters describe its position and orientation in the world. This is the first step we need to perform before doing anything else.
ROS provides a package called `camera_calibration` which provides us an easy way to determine the 11 camera parameters, which works in both simulations and for real cameras. 

https://user-images.githubusercontent.com/5123355/146292617-82fc9390-a4c4-4a6f-84f5-2562a668b059.mp4

#### Running the code:
To start the camera calibration process we run the following line of code

    roslaunch vs_project camera_calibration_undistorted.launch

After running the program we get a zip file insilde which is a `.yaml` file which contains the calibrated camera parameters.

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

https://user-images.githubusercontent.com/5123355/146293235-e178b173-0be1-44b4-94e3-5fd32f0689cd.mp4

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
While its easy for the robot to move to its destination when the workspace is clear, things become more complicated when there are obstacles involved.  To tackle this problem we make a special kind of map called the occupancy grid map. 
The way it works is that the whole workspace is divided into square blocks, each block is then assigned a value of either 0 or 1 depending on whether there is an obstace or not. 0 corresponds to free space while 1 means occupied/obstacle.

### Image Slicing
Image slicing refers to dividing the workspace into multiple square blocks, the size of the blocks can be adjusted as needed. 

<img src="https://user-images.githubusercontent.com/5123355/146286159-15ef1c31-44c9-4c61-a99d-b6fe3e0adefa.png" width="600">

### Thresholding
To detect the boxes which contain the obstacles we can use to our advantage that all of the obstacles are red. By thresholding the values hsv for this shade of red we can get the boxes containing the obstacles.

In order to find the optimum threshold values in realtime, we made a tool using opencv and QT5. 

To use it run the file `determine_threshold.py`

https://user-images.githubusercontent.com/5123355/146290465-01a147b1-638d-4889-bcb7-9bf5a95d5df8.mp4

Once the optimum threshold values have been determined we add them to our `grid_map.py`. The values need to be added to line **49** and **50** i.e 

    lower = np.array([148,119,255])
    upper = np.array([179,255,255])


<img src="https://user-images.githubusercontent.com/5123355/146286716-bd71f1fd-eb04-409d-8ef2-01252df0dd7b.png " width="600">

The black color here shows the absence of the color red (the obstacle) while the greenish yellow streaks represent the detected red color. The reason we are not getting the complete box is because the color red is not uniform on the obstacles. This may be due to the lighting conditions. 


However this is not a concern and the thresholding works well enough to give an accurite binary occupancy grid map, As can be seen in the image below

<img src="https://user-images.githubusercontent.com/5123355/146288572-0a823ffe-77e2-4fef-8b71-1b361f24eb5b.png" width="600">

#### Running the code:
To generate the occupancy grid map use the command

    roslaunch vs_project grid_map.launch


## Path Planning

## Bloopers

https://user-images.githubusercontent.com/5123355/146297446-fdefb5e4-58bc-4c53-b79e-cd9d1a64e081.mp4
