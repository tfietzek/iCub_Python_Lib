"""
Created on Thu Apr 13 15:16:32 2018

@author: Torsten Fietzek

library for network functions
"""

import yarp
import numpy as np


####################################################
# general cases
####################################################

####################################################
# binocular usecase

# network and port initialization
def network_init_binocular(client_name="client", robot_name="icubSim"):
    '''
        initialize the yarp network and generate the ports for both iCub's eye cameras

        parameter: client_name -- YARP-port client prefix; default: "client"
                robot_name  -- YARP-port robot prefix; default: "icubSim"

        return: input_port_right_eye    -- port to the iCub's right eye camera
                input_port_left_eye     -- port to the iCub's left eye camera
    '''
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print('[ERROR] Please try running yarp server')
        return None, None

    # Initialization of all needed ports
    # Port for right eye image
    input_port_right_eye = yarp.Port()
    if not input_port_right_eye.open("/" + client_name + "/eyes/right"):
        print("[ERROR] Could not open right eye port!")

    if yarp.NetworkBase_exists("/" + robot_name + "/cam/right"):
        port_name_robot_right = "/" + robot_name + "/cam/right"
    elif yarp.NetworkBase_exists("/" + robot_name + "/cam/right/rgbImage:o"):
        port_name_robot_right = "/" + robot_name + "/cam/right/rgbImage:o"
    else:
        print("[ERROR] Could not find right camera port!")
        return None, None

    if not yarp.Network.connect(port_name_robot_right, "/" + client_name + "/eyes/right"):
        print("[ERROR] Could not connect input_port_right_eye!")
        return None, None

    # Port for left eye image
    input_port_left_eye = yarp.Port()
    if not input_port_left_eye.open("/" + client_name + "/eyes/left"):
        print("[ERROR] Could not open left eye port!")

    if yarp.NetworkBase_exists("/" + robot_name + "/cam/left"):
        port_name_robot_left = "/" + robot_name + "/cam/left"
    elif yarp.NetworkBase_exists("/" + robot_name + "/cam/left/rgbImage:o"):
        port_name_robot_left = "/" + robot_name + "/cam/left/rgbImage:o"
    else:
        print("[ERROR] Could not find left camera port!")
        return None, None

    if not yarp.Network.connect(port_name_robot_left, "/" + client_name + "/eyes/left"):
        print("[ERROR] Could not connect input_port_left_eye!")
        return input_port_right_eye, None

    return input_port_right_eye, input_port_left_eye


# yarp cleanup
def network_clean_binocular(port_right_eye, port_left_eye, robot_name="icubSim"):
    '''
        disconnect and close all given ports and clean the network

        parameter: port_right_eye   -- port to the iCub's right eye camera
                port_left_eye    -- port to the iCub's left eye camera
                robot_name       -- YARP-port robot prefix; default: "icubSim"
    '''
    if yarp.NetworkBase_exists("/" + robot_name + "/cam/right"):
        port_name_robot_right = "/" + robot_name + "/cam/right"
    elif yarp.NetworkBase_exists("/" + robot_name + "/cam/right/rgbImage:o"):
        port_name_robot_right = "/" + robot_name + "/cam/right/rgbImage:o"
    else:
        port_name_robot_right = ""

    # disconnect the ports
    if not yarp.Network.disconnect(port_name_robot_right, port_right_eye.getName()):
        print("[ERROR] Could not disconnect input_port_right_eye!")

    if yarp.NetworkBase_exists("/" + robot_name + "/cam/left"):
        port_name_robot_left = "/" + robot_name + "/cam/left"
    elif yarp.NetworkBase_exists("/" + robot_name + "/cam/left/rgbImage:o"):
        port_name_robot_left = "/" + robot_name + "/cam/left/rgbImage:o"
    else:
        port_name_robot_left = ""

    if not yarp.Network.disconnect(port_name_robot_left, port_left_eye.getName()):
        print("[ERROR] Could not disconnect input_port_left_eye!")

    # close the ports
    port_right_eye.close()
    port_left_eye.close()

    # close the yarp network
    yarp.Network.fini()


####################################################
# monocular usecase

# network and port initialization
def network_init_monocular(eye, client_name="client", robot_name="icubSim"):
    '''
        initialize the yarp network and generate the port for one iCub eye camera

        parameter: eye         -- port to the selected iCub's eye camera
                client_name -- YARP-port client prefix; default: "client"
                robot_name  -- YARP-port robot prefix; default: "icubSim"

        return: input_port_eye    -- port to the selected iCub's eye camera
    '''
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print("[ERROR] Please try running yarp server")
        return None

    # Initialization of all needed ports
    if eye == "l":
        side = "left"
    elif eye == "r":
        side = "right"
    else:
        print("[ERROR] No correct eye descriptor given!")
        return None

    # Port for right eye image
    input_port_eye = yarp.Port()
    if not input_port_eye.open("/" + client_name + "/eyes/" + side):
        print("[ERROR] Could not open " + side + " eye port")
        return None

    if yarp.NetworkBase_exists("/" + robot_name + "/cam/" + side):
        port_name_robot = "/" + robot_name + "/cam/" + side
    elif yarp.NetworkBase_exists("/" + robot_name + "/cam/" + side + "/rgbImage:o"):
        port_name_robot = "/" + robot_name + "/cam/" + side + "/rgbImage:o"
    else:
        print("[ERROR] Could not find " + side + " camera port!")
        return None

    if not yarp.Network.connect(port_name_robot, input_port_eye.getName()):
        print("[ERROR] Could not connect " + side + " eye port")

    return input_port_eye


# yarp cleanup
def network_clean_monocular(input_port_eye, robot_name="icubSim"):
    '''
        disconnect and close all given ports and clean the network

        parameter:  input_port_eye      -- port to the selected iCub's eye camera
                    robot_name          -- YARP-port robot prefix; default: "icubSim"
    '''

    # disconnect the port
    str_list = input_port_eye.getName().split(sep="/")
    if yarp.NetworkBase_exists("/" + robot_name + "/cam/" + str_list[-1]):
        port_name_robot = "/" + robot_name + "/cam/" + str_list[-1]
    elif yarp.NetworkBase_exists("/" + robot_name + "/cam/" + str_list[-1] + "/rgbImage:o"):
        port_name_robot = "/" + robot_name + "/cam/" + str_list[-1] + "/rgbImage:o"
    else:
        port_name_robot = ""

    if not yarp.Network.disconnect(port_name_robot, input_port_eye.getName()):
        print("[ERROR] Could not disconnect " + str_list[-1] + " eye port")

    # close the ports
    input_port_eye.close()

    # close the yarp network
    yarp.Network.fini()


####################################################
# simulator screen

# network and port initialization
def network_init_screen(client_name="client", robot_name="icubSim"):
    '''
        initialize the yarp network and generate the port for the iCub-simulator screen

        parameter:  client_name     -- YARP-port client prefix; default: "client"
                    robot_name      -- YARP-port robot prefix; default: "icubSim"

        return: output_port_screen  -- port to the screen in the iCub-simulator
    '''
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print("[ERROR] Please try running yarp server")
        return None

    # Port for the screen
    output_port_screen = yarp.Port()
    if not output_port_screen.open(client_name + "/simscreen"):
        print("[ERROR] Could not open screen port")
        return None

    if not yarp.Network.connect(client_name + "/simscreen", "/" + robot_name + "/texture/screen"):
        print("[ERROR] Could not connect to screen")
        return None

    return output_port_screen


# yarp cleanup
def network_clean_screen(screen_port, robot_name="icubSim"):
    '''
        disconnect and close  used ports and clean the network

        parameter:  screen_port     -- port to the screen in the iCub-simulator
                    robot_name      -- YARP-port robot prefix; default: "icubSim"
    '''

    if not yarp.Network.disconnect(screen_port.getName(), "/" + robot_name + "/texture/screen"):
        print("[ERROR] Could not disconnect from Screen")

    # close the ports
    screen_port.close()

    # close the yarp network
    yarp.Network.fini()


####################################################
# prepare world camera
def scene_cam_prep(client_name="client", robot_name="icubSim"):
    '''
    prepare world camera in the iCub-simulator

    return: scene_cam   -- dict containing stuff for scene cam

    '''

    # Init YARP network
    scene_cam = {}

    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print('[ERROR] Please try running yarp server')

    # Initialization of all needed ports
    # Port for scene image
    scene_cam['port'] = yarp.Port()
    if not scene_cam['port'].open("/" + client_name + "/scenecam"):
        print("[ERROR] Could not open scene camera port")
    if not yarp.Network.connect("/" + robot_name + "/cam", "/" + client_name + "/scenecam"):
        print("[ERROR] Could not connect input port scene")

    # Initialization of imgae data structures
    scene_cam['np_img'] = np.ones((240, 320, 3), np.uint8)
    scene_cam['y_img'] = yarp.ImageRgb()
    scene_cam['y_img'].resize(320, 240)

    scene_cam['y_img'].setExternal(scene_cam['np_img'].data, scene_cam['np_img'].shape[1], scene_cam['np_img'].shape[0])

    return scene_cam


####################################################
# special cases
####################################################

####################################################
# network and port initialization
def network_initial():
    '''
        initialize the yarp network and generate the ports for the simulator screen and both iCub's eye cameras

        return: output_port_screen      -- port to the screen in the iCub-simulator
                input_port_right_eye    -- port to the iCub's right eye camera
                input_port_left_eye     -- port to the iCub's left eye camera
    '''
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print("[ERROR] Please try running yarp server")
        return None, None, None

    # Initialization of all needed ports

    # Port for right eye image
    input_port_right_eye = yarp.Port()
    input_port_right_eye.open("/eyes/right")
    if not yarp.Network.connect("/icubSim/cam/right", "/eyes/right"):
        print("[ERROR] Could not connect input_port_right_eye")
        return None, None, None

    # Port for left eye image
    input_port_left_eye = yarp.Port()
    input_port_left_eye.open("/eyes/left")
    if not yarp.Network.connect("/icubSim/cam/left", "/eyes/left"):
        print("[ERROR] Could not connect input_port_left_eye")
        return None, input_port_right_eye, None

    # Port for the screen
    output_port_screen = yarp.Port()
    output_port_screen.open("/simscreen")
    if not yarp.Network.connect("/simscreen", "/icubSim/texture/screen"):
        print("[ERROR] Could not connect to screen")
        return None, input_port_right_eye, input_port_left_eye

    return output_port_screen, input_port_right_eye, input_port_left_eye


# yarp cleanup
def network_clean(screen_port, port_right_eye, port_left_eye):
    '''
        disconnect and close all used ports and clean the network

        return: screen_port         -- port to the screen in the iCub-simulator
                port_right_eye      -- port to the iCub's right eye camera
                port_left_eye       -- port to the iCub's left eye camera
    '''
    # disconnect the ports
    if not yarp.Network.disconnect("/simscreen", "/icubSim/texture/screen"):
        print("[ERROR] Could not disconnect from Screen")

    if not yarp.Network.disconnect("/icubSim/cam/right", "/eyes/right"):
        print("[ERROR] Could not disconnect right eye port")

    if not yarp.Network.disconnect("/icubSim/cam/left", "/eyes/left"):
        print("[ERROR] Could not disconnect left eye port")

    # close the ports
    screen_port.close()
    port_right_eye.close()
    port_left_eye.close()

    # close the yarp network
    yarp.Network.fini()


####################################################
# network and port initialization, only right eye
def network_initial_only_right():
    '''
        initialize the yarp network and generate the ports for the simulator screen and the iCub's right eye camera

        return: output_port_screen      -- port to the screen in the iCub-simulator
                input_port_right_eye    -- port to the iCub's right eye camera
    '''
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print("[ERROR] Please try running yarp server")
        return None, None

    # Initialization of all needed ports

    # Port for right eye image
    input_port_right_eye = yarp.Port()
    input_port_right_eye.open("/eyes/right")
    if not yarp.Network.connect("/icubSim/cam/right", "/eyes/right"):
        print("[ERROR] Could not connect right eye port")

    # Port for the screen
    output_port_screen = yarp.Port()
    output_port_screen.open("/Grabber")
    if not yarp.Network.connect("/Grabber", "/icubSim/texture/screen"):
        print("[ERROR] Could not connect Grabber to Texture")

    return output_port_screen, input_port_right_eye


# yarp cleanup, only right eye
def network_clean_only_right(screen_port, port_right_eye):
    '''
        disconnect and close all used ports and clean the network

        parameter:  screen_port         -- port to the screen in the iCub-simulator
                    port_right_eye      -- port to the iCub's right eye camera
    '''

    # disconnect the ports
    if not yarp.Network.disconnect("/Grabber", "/icubSim/texture/screen"):
        print("[ERROR] Could not disconnect Grabber to Texture")

    if not yarp.Network.disconnect("/icubSim/cam/right", "/eyes/right"):
        print("[ERROR] Could not disconnect right eye port")

    # close the ports
    screen_port.close()
    port_right_eye.close()

    # close the yarp network
    yarp.Network.fini()
