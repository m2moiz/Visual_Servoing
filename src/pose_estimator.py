#!/usr/bin/env python3

import rospy 
from sensor_msgs.msg import Image 
from vs_project.msg import my_robot_pose
from std_msgs.msg import Float64MultiArray
import cv2 
import numpy as np
from cv_bridge import CvBridge
import yaml

debug = 0

def extract_param_from_yaml(yaml_file):
	with open(yaml_file, "r") as data:
		try:
			calibration_data = yaml.safe_load(data)
		except yaml.YAMLError as exc:
			print(exc)
	camera_matrix = calibration_data["camera_matrix"]
	distortion_coef = calibration_data["distortion_coefficients"]
	height = calibration_data["image_width"]
	width = calibration_data["image_height"]
	projection_matrix = np.array(camera_matrix["data"]).reshape((camera_matrix["rows"],camera_matrix["cols"]))
	lens_distortion = np.array(distortion_coef["data"]).reshape((distortion_coef["rows"],distortion_coef["cols"]))
	return lens_distortion,projection_matrix,height,width

def homogeneous_from_vectors(translation_vectors, rotation_vectors):
  tmat = np.array(translation_vectors)
  rmat, _ = cv2.Rodrigues(rotation_vectors)
  hmat = np.r_['0,2', np.c_[rmat, tmat.T], [0, 0, 0, 1]]
  return np.array(hmat)

def estimate_aruco_pose(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients):
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  cv2.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)
  parameters = cv2.aruco.DetectorParameters_create()
  global homo_mat, rvec, tvec

  corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict,parameters=parameters,
      cameraMatrix=matrix_coefficients,
      distCoeff=distortion_coefficients)
 

  if len(corners) > 0:
    for index, id in enumerate(ids):
      rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[index], 0.14, matrix_coefficients, distortion_coefficients)
      cv2.aruco.drawDetectedMarkers(frame, corners) 
      # Draw Axis
      cv2.aruco.drawAxis(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.1)
      #Getting the transformation matrix from the rotation and translation vectors
      homo_mat = homogeneous_from_vectors(tvec[0][0], rvec[0][0])
  return frame, homo_mat, rvec, tvec

def callback(data):
  received_image = np.frombuffer(data.data, dtype=np.uint8).reshape(data.height, data.width, -1)
  
  h,  w = received_image.shape[:2]
  newcameramtx, roi = cv2.getOptimalNewCameraMatrix(projection_matrix, lens_distortion_param, (im_width,im_height), 1, (im_width,im_height))
  
  # removing distortion form the image
  undistorted_image = cv2.undistort(received_image, projection_matrix, lens_distortion_param, None, newcameramtx)
  
  # resize the image
  x, y, w, h = roi
  undistort_frame = undistorted_image[y:y+h, x:x+w]
  
  #Defining the type of aruco marker used
  aruco_dict_type = cv2.aruco.DICT_ARUCO_ORIGINAL 
  output, hmat, rot_vec, tra_vec = estimate_aruco_pose(undistort_frame, aruco_dict_type, projection_matrix, lens_distortion_param)

  #Publishing the rotation and translation vectors
  custom_message.rotation.x, custom_message.rotation.y, custom_message.rotation.z  = rot_vec[0][0][0], rot_vec[0][0][1], rot_vec[0][0][2]
  custom_message.translation.x, custom_message.translation.y, custom_message.translation.z = tra_vec[0][0][0], tra_vec[0][0][1], tra_vec[0][0][2]
  current_pub.publish(custom_message)

  #Publishing the transformation matrix
  homogenous_matrix.data = hmat.flatten()
  homo_mat_pub.publish(homogenous_matrix)

  image_message = bridge.cv2_to_imgmsg(output, encoding="rgb8")
  image_publisher.publish(image_message)
      
if __name__ == '__main__': 
  # Loading the camera calibration file
  camera_yaml_filepath = rospy.get_param('yaml_file')
  lens_distortion_param, projection_matrix, im_height, im_width = extract_param_from_yaml(camera_yaml_filepath)

  # Initializing node
  rospy.init_node('pose_estimator', anonymous=True)

  custom_message = my_robot_pose()
  homogenous_matrix = Float64MultiArray()
  bridge = CvBridge()

  #Publishing to the topics
  current_pub = rospy.Publisher('current_position', my_robot_pose, queue_size=8)
  homo_mat_pub = rospy.Publisher('current_homo_matrix', Float64MultiArray, queue_size=8)

  image_publisher = rospy.Publisher('image_aruco_detected', Image, queue_size=8)

  #Subscribing to the image topic
  camera = rospy.get_param('camera')
  # print(camera)
  rospy.Subscriber(camera, Image, callback)

  rospy.spin()
