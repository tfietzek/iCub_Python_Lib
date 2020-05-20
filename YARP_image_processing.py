"""
Created on Thu Apr 13 15:16:32 2018

@author: tofo

library for YARP image processing functions
"""

import time

import numpy as np
import yarp


####################################################
######### Initialization of the eye images #########
def define_eye_imgs():
    '''
    Initialization of both eye images

    return: right_eye_yarp_image    -- yarp image for the right eye image
            right_eye_img_array     -- np array for the right eye image
            left_eye_yarp_image     -- yarp image for the left eye image
            left_eye_img_array      -- np array for the left eye image
    '''
    # Create np array to receive the image and the YARP image wrapped around it
    left_eye_img_array = np.ones((240, 320, 3), np.uint8)
    left_eye_yarp_image = yarp.ImageRgb()
    left_eye_yarp_image.resize(320, 240)

    right_eye_img_array = np.ones((240, 320, 3), np.uint8)
    right_eye_yarp_image = yarp.ImageRgb()
    right_eye_yarp_image.resize(320, 240)

    left_eye_yarp_image.setExternal(
        left_eye_img_array.data, left_eye_img_array.shape[1], left_eye_img_array.shape[0])
    right_eye_yarp_image.setExternal(
        right_eye_img_array.data, right_eye_img_array.shape[1], right_eye_img_array.shape[0])

    return right_eye_yarp_image, right_eye_img_array, left_eye_yarp_image, left_eye_img_array


####################################################
######### Initialization of one eye image ##########
def define_eye_img():
    '''
    Initialization of one eye image

    return: right_eye_yarp_image    -- yarp image for the eye image
            right_eye_img_array     -- np array for the eye image
    '''
    # Create np array to receive the image and the YARP image wrapped around it
    eye_img_array = np.ones((240, 320, 3), np.uint8)

    eye_yarp_image = yarp.ImageRgb()
    eye_yarp_image.resize(320, 240)
    eye_yarp_image.setExternal2(
        eye_img_array.data, eye_img_array.shape[1], eye_img_array.shape[0])

    return eye_yarp_image, eye_img_array


####################################################
######## read and convert robot eye images #########
def read_robot_eyes(port_right_eye, port_left_eye, right_eye_yarp_image, left_eye_yarp_image, right_eye_img_array, left_eye_img_array):
    '''
    read and convert both robot eye images

    params: port_right_eye          -- input port from the right eye camera
            port_left_eye           -- input port from the left eye camera
            right_eye_yarp_image    -- yarp image for the right eye image
            left_eye_yarp_image     -- yarp image for the left eye image
            right_eye_img_array     -- np array for the right eye image
            left_eye_img_array      -- np array for the left eye image
    return: right_eye_img_array     -- np array now containing the right eye image
            left_eye_img_array      -- np array now containing the left eye image
    '''
    # Read the images from the robot cameras
    port_left_eye.read(left_eye_yarp_image)
    port_left_eye.read(left_eye_yarp_image)
    port_right_eye.read(right_eye_yarp_image)
    port_right_eye.read(right_eye_yarp_image)

    if left_eye_yarp_image.getRawImage().__int__() != left_eye_img_array.__array_interface__['data'][0]:
        print("read() reallocated my left_eye_yarp_image!")
    if right_eye_yarp_image.getRawImage().__int__() != right_eye_img_array.__array_interface__['data'][0]:
        print("read() reallocated my right_eye_yarp_image!")

    return right_eye_img_array, left_eye_img_array


####################################################
######### read and convert robot eye image #########
def read_robot_eye(port_eye, eye_yarp_image, eye_img_array):
    '''
    read and convert one robot eye image

    params: port_eye        -- input port from the eye camera
            eye_yarp_image  -- yarp image for the eye image
            eye_img_array   -- np array for the eye image
    return: eye_img_array   -- np array now containing the eye image
    '''
    # Read the images from the robot camera
#    time_transfer = time.time()
    port_eye.read(eye_yarp_image)
    port_eye.read(eye_yarp_image)
    time.sleep(0.03)

    if eye_yarp_image.getRawImage().__int__() != eye_img_array.__array_interface__['data'][0]:
        print("read() reallocated my yarp_image!")

#    time_transfer = time.time() - time_transfer
    # print 'time transfer image from iCub:', round(time_transfer, 4)

    return eye_img_array


####################################################
############### show image on screen ###############
def show_image(screen_port, image):
    '''
    show image on the screen in the iCub-simulator

    params: screen_port     -- input port of the screen
            image           -- image to be shown on the screen
    '''
    # show the image on the screen
#    time_transfer = time.time()
    screen_port.write(image)
    time.sleep(0.03)
#    time_transfer = time.time() - time_transfer
    # print 'time transfer image to screen:', round(time_transfer, 4)
