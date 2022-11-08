"""
Created on Mon May 04 2020

@author: Torsten Fietzek

transformation matrices for the iCub and the Gazebo- and iCub-Simulator
"""

import numpy as np

######################################################################
######################## Simulation parameter ########################
gazebo_sim = True

######################################################################
###################### Transformation matrices: ######################
###### iCub_Sim coordinate system <-> gazebo coordinate system #######
Transfermat_gazebo2iCubSim = np.array([ [  0.,  1., 0.,  0.0000 ],
                                        [  0.,  0., 1.,  0.0000 ],
                                        [  1.,  0., 0.,  0.0000 ],
                                        [  0.,  0., 0.,  1.0000 ]])
Transfermat_iCubSim2gazebo = np.linalg.inv(Transfermat_gazebo2iCubSim)

######## robot coordinate system <-> gazebo coordinate system ########
Transfermat_robot2gazebo = np.array([   [ -1.,  0., 0.,  0.0000 ],
                                        [  0., -1., 0.,  0.0000 ],
                                        [  0.,  0., 1.,  0.6000 ],
                                        [  0.,  0., 0.,  1.0000 ]])
Transfermat_gazebo2robot = np.linalg.inv(Transfermat_robot2gazebo)

####### robot coordinate system <-> iCub_Sim coordinate system #######
Transfermat_robot2iCubSim = np.array([  [  0., -1., 0.,  0.0000 ],
                                        [  0.,  0., 1.,  0.5976 ],
                                        [ -1.,  0., 0., -0.0260 ],
                                        [  0.,  0., 0.,  1.0000 ]])
Transfermat_iCubSim2robot = np.linalg.inv(Transfermat_robot2iCubSim)

if gazebo_sim:
    Transfermat_robot2world = Transfermat_robot2gazebo
    Transfermat_world2robot = Transfermat_gazebo2robot
else:
    Transfermat_robot2world = Transfermat_robot2iCubSim
    Transfermat_world2robot = Transfermat_iCubSim2robot


######################################################################
############### Initial hand position and orientation ################
pos_hand_world_coord   = np.array([ -0.15, 0.8, 0.2, 1.0 ])             # in world coordinate system
init_hand_pos_robot_rf = np.dot(Transfermat_iCubSim2robot, pos_hand_world_coord.reshape((4,1))) # in robot coordinate system
orientation_robot_hand = np.array([ 0.0022, -0.993, -0.1178, 2.0423 ])  # in robot coordinate system

def transform_position(pos, mat):
    pos = np.array(pos)
    if pos.shape[0] == 3:
        shape = (1,)
        if len(pos.shape) == 2:
            if pos.shape[1] > 0:
                shape = (1, pos.shape[1])
        pos = np.concatenate((pos, np.array([1.]).reshape(shape)))
        pos = pos.reshape((4,1))
        return np.dot(mat, pos)[0:3,0]
    elif pos.shape[0] == 4:
        pos = pos.reshape((4,1))
        return np.dot(mat, pos)[0:3,0]
    else:
        print("Check position vector dimension!", pos.shape)

def retrieve_world_transform(use_gazebo):
    if use_gazebo:
        Transfermat_robot2world = Transfermat_robot2gazebo
        Transfermat_world2robot = Transfermat_gazebo2robot
    else:
        Transfermat_robot2world = Transfermat_robot2iCubSim
        Transfermat_world2robot = Transfermat_iCubSim2robot
    return Transfermat_robot2world, Transfermat_world2robot
