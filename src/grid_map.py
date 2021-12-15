#!/usr/bin/env python

import rospy 
import matplotlib.pyplot as plt
import cv2
import numpy as np
from std_msgs.msg import Int32MultiArray


def img_to_grid(img, row, col):
    ww = [[i.min(), i.max()] for i in np.array_split(range(img.shape[0]),row)]
    hh = [[i.min(), i.max()] for i in np.array_split(range(img.shape[1]),col)]
    grid = [img[j:jj,i:ii,:] for j,jj in ww for i,ii in hh]
    # print(ww)
    return grid, len(ww), len(hh)

def plot_grid_img(grid,row,col,h=10,w=10):
    fig, ax = plt.subplots(nrows=row, ncols=col)
    [axi.set_axis_off() for axi in ax.ravel()]
    fig.set_figheight(h)
    fig.set_figwidth(w)
    c = 0
    for row in ax:
        for col in row:
            col.imshow(np.flip(grid[c],axis=-1))
            c+=1
    plt.show(block=False)


def plot_grid_mask(grid,row,col,h=10,w=10):
    fig, ax = plt.subplots(nrows=row, ncols=col)
    [axi.set_axis_off() for axi in ax.ravel()]

    fig.set_figheight(h)
    fig.set_figwidth(w)
    c = 0
    for row in ax:
        for col in row:
            col.imshow(grid[c])
            c+=1
    plt.show()


def find_obstacle(obstacle):
    obs_index = []
    mask_mat = []
    for i in range(len(obstacle)):
        image = cv2.cvtColor(obstacle[i], cv2.COLOR_BGR2HSV)
        lower = np.array([148,119,255])
        upper = np.array([179,255,255])
        mask = cv2.inRange(image, lower, upper)
        mask_mat.append(mask)
        if cv2.countNonZero(mask) > 0:
         obs_index.append(i)
        #  cv2.imshow('mask{}'.format(i), mask)
    return mask_mat, obs_index

def occupancy_array(r,c,iden):
    occ_arr = []
    for i in range(r*c):
        occ_arr.append(0) 
    for j in range(len(iden)):
        occ_arr[iden[j]] = 1
    return occ_arr




if __name__=='__main__':
    rospy.init_node('occupancy_grid_map', anonymous=True)

    grid_map = Int32MultiArray()
    grid_map_pub = rospy.Publisher('grid_map_calculated', Int32MultiArray, latch=True, queue_size=8)
    

    img = cv2.imread("/home/moiz/catkin_ws/src/vs_project/parking1.png")
    row, col =10,10
    grid , r,c = img_to_grid(img,row,col)
    mask_mat, id = find_obstacle(grid)

    occupancy = occupancy_array(row,col,id)
    grid_map.data = occupancy
    grid_map_pub.publish(grid_map)

    plot_grid_img(grid,r,c)
    plot_grid_mask(mask_mat,r,c)

    rospy.spin()
    cv2.waitKey()

