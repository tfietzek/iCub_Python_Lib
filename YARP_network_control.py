"""
Created on Thu Apr 13 15:16:32 2018

@author: tofo

library for network functions
"""

import yarp

####################################################
######### network and port initialization ##########


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
        print("[error] Please try running yarp server")
        quit()

    # Initialization of all needed ports

    # Port for right eye image
    input_port_right_eye = yarp.Port()
    input_port_right_eye.open("/eyes/right")
    if not yarp.Network.connect("/icubSim/cam/right", "/eyes/right"):
        print("[error] Could not connect input_port_right_eye")
        quit()

    # Port for left eye image
    input_port_left_eye = yarp.Port()
    input_port_left_eye.open("/eyes/left")
    if not yarp.Network.connect("/icubSim/cam/left", "/eyes/left"):
        print("[error] Could not connect input_port_left_eye")
        quit()

    # Port for the screen
    output_port_screen = yarp.Port()
    output_port_screen.open("/simscreen")
    if not yarp.Network.connect("/simscreen", "/icubSim/texture/screen"):
        print("[error] Could not connect to screen")
        quit()

    return output_port_screen, input_port_right_eye, input_port_left_eye


####################################################
################### yarp cleanup ###################
def network_clean(screen_port, port_right_eye, port_left_eye):
    '''
    disconnect and close all used ports and clean the network

    return: screen_port         -- port to the screen in the iCub-simulator
            port_right_eye      -- port to the iCub's right eye camera
            port_left_eye       -- port to the iCub's left eye camera
    '''
    # disconnect the ports
    if not yarp.Network.disconnect("/simscreen", "/icubSim/texture/screen"):
        print("[error] Could not disconnect from Screen")
        quit()
    if not yarp.Network.disconnect("/icubSim/cam/right", "/eyes/right"):
        print("[error] Could not disconnect input_port_right_eye")
        quit()
    if not yarp.Network.disconnect("/icubSim/cam/left", "/eyes/left"):
        print("[error] Could not disconnect input_port_left_eye")
        quit()

    # close the ports
    screen_port.close()
    port_right_eye.close()
    port_left_eye.close()

    # close the yarp network
    yarp.Network.fini()


####################################################
# network and port initialization, only right eye ##
def network_initial_only_right():
    '''
    initialize the yarp network and generate the ports for the simulator screen and the iCub's right eye camera

    return: output_port_screen      -- port to the screen in the iCub-simulator
            input_port_right_eye    -- port to the iCub's right eye camera
    '''
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print("[error] Please try running yarp server")
        quit()

    # Initialization of all needed ports

    # Port for right eye image
    input_port_right_eye = yarp.Port()
    input_port_right_eye.open("/eyes/right")
    if not yarp.Network.connect("/icubSim/cam/right", "/eyes/right"):
        print("[error] Could not connect input_port_right_eye")
        quit()

    # Port for the screen
    output_port_screen = yarp.Port()
    output_port_screen.open("/Grabber")
    if yarp.Network.connect("/Grabber", "/icubSim/texture/screen") != True:
        print("[error] Could not connect Grabber to Texture")
        quit()

    return output_port_screen, input_port_right_eye


####################################################
########### yarp cleanup, only right eye ###########
def network_clean_only_right(screen_port, port_right_eye):
    '''
    disconnect and close all used ports and clean the network

    return: screen_port         -- port to the screen in the iCub-simulator
            port_right_eye      -- port to the iCub's right eye camera
    '''
    # disconnect the ports
    if not yarp.Network.disconnect("/Grabber", "/icubSim/texture/screen"):
        print("[error] Could not disconnect Grabber to Texture")
        quit()
    if not yarp.Network.disconnect("/icubSim/cam/right", "/eyes/right"):
        print("[error] Could not disconnect input_port_right_eye")
        quit()

    # close the ports
    screen_port.close()
    port_right_eye.close()

    # close the yarp network
    yarp.Network.fini()


####################################################


####################################################
######### network and port initialization ##########
def network_init_binocular():
    '''
    initialize the yarp network and generate the ports for the simulator screen and both iCub's eye cameras

    return: input_port_right_eye    -- port to the iCub's right eye camera
            input_port_left_eye     -- port to the iCub's left eye camera
    '''
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print("[error] Please try running yarp server")
        quit()

    # Initialization of all needed ports

    # Port for right eye image
    input_port_right_eye = yarp.Port()
    input_port_right_eye.open("/eyes/right")
    if not yarp.Network.connect("/icubSim/cam/right", "/eyes/right"):
        print("[error] Could not connect right eye port")
        quit()

    # Port for left eye image
    input_port_left_eye = yarp.Port()
    input_port_left_eye.open("/eyes/left")
    if not yarp.Network.connect("/icubSim/cam/left", "/eyes/left"):
        print("[error] Could not connect left eye port")
        quit()

    return input_port_right_eye, input_port_left_eye


####################################################
################### yarp cleanup ###################
def network_clean_binocular(port_right_eye, port_left_eye):
    '''
    disconnect and close all used ports and clean the network

    return: port_right_eye      -- port to the iCub's right eye camera
            port_left_eye       -- port to the iCub's left eye camera
    '''
    # disconnect the ports
    if not yarp.Network.disconnect("/icubSim/cam/right", "/eyes/right"):
        print("[error] Could not disconnect right eye port")
        quit()
    if not yarp.Network.disconnect("/icubSim/cam/left", "/eyes/left"):
        print("[error] Could not disconnect left eye port")
        quit()

    # close the ports
    port_right_eye.close()
    port_left_eye.close()

    # close the yarp network
    yarp.Network.fini()

####################################################
######### network and port initialization ##########


def network_init_monocular():
    '''
    initialize the yarp network and generate the ports for the simulator screen and both iCub's eye cameras

    return: input_port_right_eye    -- port to the iCub's right eye camera
    '''
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print("[error] Please try running yarp server")
        quit()

    # Initialization of all needed ports

    # Port for right eye image
    input_port_right_eye = yarp.Port()
    input_port_right_eye.open("/eyes/right")
    if not yarp.Network.connect("/icubSim/cam/right", "/eyes/right"):
        print("[error] Could not connect right eye port")
        quit()

    return input_port_right_eye


####################################################
################### yarp cleanup ###################
def network_clean_monocular(port_right_eye):
    '''
    disconnect and close all used ports and clean the network

    return: port_right_eye      -- port to the iCub's right eye camera
            port_left_eye       -- port to the iCub's left eye camera
    '''
    # disconnect the ports
    if not yarp.Network.disconnect("/icubSim/cam/right", "/eyes/right"):
        print("[error] Could not disconnect right eye port")
        quit()

    # close the ports
    port_right_eye.close()

    # close the yarp network
    yarp.Network.fini()

####################################################
