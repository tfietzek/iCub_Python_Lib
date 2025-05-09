"""
Created on Thu Apr 13 15:16:32 2018

@author: Torsten Fietzek

Module containing methods facilitating iCub motor control
-> based on YAPR-Python bindings
"""

import time

import numpy as np
import yarp


parts = {"head": True, "left_arm": False, "right_arm": False,
         "torso": True, "right_leg": False, "left_leg": False}


######################################################################
# Init motor control interfaces

# Joint based control interfaces -> joint angles/velocities
def motor_init(part, control="position", robot_prefix="icubSim", client_prefix="client"):
    '''
        initialize motor control for the given part

        params: part            -- part of the iCub to be controlled (string: head, left_arm, right_arm, torso, right_leg, left_leg)
                control         -- control type: position(default) -> joint angle control ; velocity -> joint velocity control
                robot_prefix    -- robot name; normally "iCubSim" for simulation and "icub" for real robot
                client_prefix   -- client name; normally no need to change; only if multiple user work in the same YARP-network

        return: iPos    -- Position/Velocity Controller for the given iCub part
                iEnc    -- Encoder for the controlled joints
                jnts    -- number of controlled joints
                driver  -- device driver; need to be returned, otherwise joint controlboard is closed

                Returns None for all if an error occured
    '''

    if part not in parts:
        print("Error: No correct part descriptor!")
        return None, None, None, None

    # prepare a property object
    props = yarp.Property()
    props.put("device", "remote_controlboard")
    props.put("local", "/" + client_prefix + "/" + control + "/" + part)
    props.put("remote", "/" + robot_prefix + "/" + part)

    # create remote driver
    driver = yarp.PolyDriver(props)

    if driver is None:
        print("Error: Motor initialization failed!")
        return None, None, None, None

    # query motor control interfaces
    if control == "position":
        iCtrl = driver.viewIPositionControl()
    elif control == "velocity":
        iCtrl = driver.viewIVelocityControl()
    iEnc = driver.viewIEncoders()

    if iCtrl is None:
        print("Error: Motor initialization failed!")
        return None, None, None, None

    # retrieve number of joints
    jnts = iCtrl.getAxes()

    print('----- Controlling', jnts, 'joints -----')
    return iCtrl, iEnc, jnts, driver


# Cartesian control interface -> cartesian poses for hand/foot
def motor_init_cartesian(part, ctrl_prior="position", robot_prefix="icubSim", client_prefix="client"):
    '''
        initialize cartesian controller for the given part
        -> position needs to be given in robot reference frame

        params: part            -- part of the iCub to be controlled (string: left_arm, right_arm, right_leg, left_leg)
                ctrl_prior      -- control priority; either position or orientation of the end-effector (hand or foot)
                robot_prefix    -- robot name; normally "iCubSim" for simulation and "icub" for real robot
                client_prefix   -- client name; normally no need to change; only if multiple user work in the same YARP-network

        return: iCart   -- Cartesian Controller for the given iCub part -> None in case of failure
                driver  -- device driver; need to be returned, otherwise joint controlboard is closed -> None in case of failure
    '''

    if part not in parts or parts[part]:
        print("Error: No correct part descriptor!")
        return None, None

    # Prepare a property object
    props = yarp.Property()
    props.put("device", "cartesiancontrollerclient")
    props.put("remote", "/" + robot_prefix + "/cartesianController/" + part)
    props.put("local", "/cart/" + client_prefix + "/" + part)

    # Create remote driver
    driver = yarp.PolyDriver(props)

    if driver is None:
        print("Error: Motor initialization failed!")
        return None, None

    # Query motor control interfaces
    iCart = driver.viewICartesianControl()
    iCart.setPosePriority(ctrl_prior)
    time.sleep(1)

    return iCart, driver


# Gaze controller interface for eye/head movements -> cartesian/image positions
def gazectrl_init(client_prefix="client"):
    '''
        initialize gaze controller device
        -> position needs to be given in robot reference frame

        params: robot_prefix    -- robot name; normally "iCubSim" for simulation and "icub" for real robot
                client_prefix   -- client name; normally no need to change; only if multiple user work in the same YARP-network

        return: igaze   -- gaze controller interface
                driver  -- device driver; need to be returned, otherwise joint controlboard is closed

                Returns None for all if an error occured
    '''

    # prepare a property object
    props = yarp.Property()
    props.put("device", "gazecontrollerclient")
    props.put("local", "/" + client_prefix + "/gazectrl")
    props.put("remote", "/iKinGazeCtrl")

    # create remote driver
    driver = yarp.PolyDriver(props)

    if driver is None:
        print("Error: Motor initialization failed!")
        return None, None

    print("open gaze controller")
    if driver.isValid():
        iGaze = driver.viewIGazeControl()
    else:
        return None, None

    return iGaze, driver


######################################################################
# Joint position control methods

# Go to head zero position
def goto_zero_head_pos(iPos_head, iEnc_head, jnts_head):
    '''
        go to the all joints at 0 degree position

        params: iPos_head   -- Position Controller for the iCub head
                iEnc_head   -- Encoder for the head joints
                jnts_head   -- number of head joints
    '''

    zero_pos = set_pos_vector_same(0.0, jnts_head)
    motion = not iPos_head.positionMove(zero_pos.data())
    while not motion:
        act_pos = get_joint_position(iEnc_head, jnts_head, as_np=True)
        motion = iPos_head.checkMotionDone()
        #  and np.allclose(act_pos, yarpvec_2_npvec(zero_pos), atol=0.25)

        # motion = iPos_head.checkMotionDone() and ((np.abs(act_pos)).sum() < 0.2)


######################################################################
# Move a single joint of controlled part to a new position
def goto_position_block_single(iPos, jnt, position):
    '''
        Go to given position and block until motion done

        params: iPos        -- Position Controller for the iCub part
                jnt         -- controlled joint -> single joint
                position    -- new position -> single value
    '''
    motion = not (iPos.positionMove(jnt, position))
    yarp.delay(0.01)
    # optional, for blocking while moving the joints
    while not motion:
        motion = iPos.checkMotionDone()


# Move a multiple joints of controlled part to a new position
def goto_position_block_multi(iPos, jnts, position):
    '''
        Go to given position and block until motion done

        params: iPos        -- Position Controller for the iCub part
                jnt         -- controlled joints -> 1D (int) array
                position    -- new position -> 1D (double) array
    '''
    jnts = np.array(jnts)
    joints = yarp.VectorInt(jnts.shape[0])
    for i in range(joints.size()):
        joints.set(i, jnts[i])

    if not isinstance(position, yarp.Vector):
        position = npvec_2_yarpvec(position)

    motion = not (iPos.positionMove(3, joints.data(), position.data()))
    # optional, for blocking while moving the joints
    while not motion:
        motion = iPos.checkMotionDone()


# Move all joints of controlled part to a new position
def goto_position_block(iPos, iEnc, jnts, position):
    '''
        Go to given position and block until motion done

        params: iPos        -- Position Controller for the iCub part
                iEnc        -- Encoder for the joints
                jnts        -- number of controlled joints
                position    -- new position -> 1D
    '''

    if not isinstance(position, yarp.Vector):
        position = npvec_2_yarpvec(position)

    motion = not iPos.positionMove(position.data())
    while not motion:
        act_pos = get_joint_position(iEnc, jnts, as_np=True)
        motion = iPos.checkMotionDone()
        # and np.allclose(act_pos, yarpvec_2_npvec(position), atol=0.5)


######################################################################
# Move eyes to new position
def move_eyes(eye_pos, iPos_h, jnts_h, offset_h=0.0):
    '''
        move the iCub eyes to a new position

        params: eye_pos     -- target eye position [ gaze_y, gaze_x, vergence_angle ]
                iPos_h      -- Position Controller for the iCub head
                jnts_h      -- number of head joints
                offset_h    -- head offset in left/right direction
    '''
    targ_pos = set_pos_vector_same(0.0, jnts_h)
    targ_pos.set(2, offset_h)
    targ_pos.set(3, eye_pos[0])
    targ_pos.set(4, (eye_pos[1] - offset_h))
    targ_pos.set(5, eye_pos[2])

    motion = iPos_h.positionMove(targ_pos.data())
    while not motion:
        time.sleep(0.01)
        motion = iPos_h.checkMotionDone()
    time.sleep(0.1)


######################################################################
# Get joint angles of the controlled part
def get_joint_position(iEnc, jnts, as_np=False):
    '''
        get position of controlled joints

        params: iEnc        -- Encoder for the controlled joints
                jnts        -- number of joints
                as_np       -- if True: a numpy array is returned
                                  False: a YARP vector is returned

        return: vector containing the joint positions -> YARP-Vector or numpy array dependent on as_np
    '''
    # read encoders
    yarp_angles = yarp.Vector(jnts)
    read = iEnc.getEncoders(yarp_angles.data())
    while not read:
        time.sleep(0.01)
        read = iEnc.getEncoders(yarp_angles.data())
    if as_np:
        return yarpvec_2_npvec(yarp_angles)
    return yarp_angles


######################################################################
# Map motor control to dictionary
def create_motor_dict(parts_used):
    '''
        wrap the motor control interfaces in a dictionary for a given set of robot parts
        (Used to connect the CPG to the iCub)

        params: parts_used      -- list with strings for the used robot parts

        return: joint_mapping   -- mapping of the part joint numbers to a sequence containing all joints
                ctrl_interfaces -- dictionary for all control interfaces
                motor_driver    -- list with all created device drivers
    '''

    joint_mapping = {}
    ctrl_interfaces = {}
    motor_driver = []
    sequence = {"head": 6, "torso": 3, "right_arm": 16,
                "right_leg": 6, "left_arm": 16, "left_leg": 6}
    j = 0
    for key in sequence:
        if key in parts_used:
            iCtrl, iEnc, jnts, driver = motor_init(key, client_prefix="CPG")
            if driver is not None:
                if jnts != sequence[key]:
                    print("Error while motor initialization of part:", key)
                    break
                motor_driver.append((key, driver))
                for i in range(j, j + sequence[key]):
                    joint_mapping[str(i)] = key
                    ctrl_interfaces[key] = (iCtrl, iEnc, jnts)
                j += sequence[key]

    return joint_mapping, ctrl_interfaces, motor_driver


######################################################################
# Gazecontroller methods

def gz_block_head(iGaze):
    '''
        block neck motion for gaze control

        params: igaze   -- gaze controller interface

        return: True/False dependent on success/failure
    '''
    return iGaze.blockNeckRoll() & iGaze.blockNeckYaw() & iGaze.blockNeckPitch()


def look_at_3Dpoint(iGaze, point_rrf):
    '''
        look at a given fixation point

        params: iGaze       -- gaze controller interface
                point_rrf   -- point coordinates in robot reference frame (list/numpy array)

        return: True/False dependent on success/failure
    '''
    if iGaze.lookAtFixationPoint(npvec_2_yarpvec(point_rrf)):
        return iGaze.waitMotionDone(period=0.1, timeout=5.)
    else:
        print("Gaze controller failed!")
        return False


######################################################################
# Set YARP position vector with given values

def set_pos_vector(pos_vec, val_j0, val_j1, val_j2, val_j3, val_j4, val_j5):
    '''
        set position vector with given values for each joint (6 joints like iCub head)

        params: pos_vec     -- YARP position vector
                val_j0      -- value joint 0, double value
                val_j1      -- value joint 1, double value
                val_j2      -- value joint 2, double value
                val_j3      -- value joint 3, double value
                val_j4      -- value joint 4, double value
                val_j5      -- value joint 5, double value

        return: pos_vec     -- position as YARP vector
    '''
    pos_vec.set(0, val_j0)
    pos_vec.set(1, val_j1)
    pos_vec.set(2, val_j2)
    pos_vec.set(3, val_j3)
    pos_vec.set(4, val_j4)
    pos_vec.set(5, val_j5)

    return pos_vec


def set_pos_vector_array(position, jnts):
    '''
        set position vector with given values for each joint (e.g. 6 joints for iCub head)

        params: position    -- position in array-like structure (list/numpy array), double values
                jnts        -- number of joints

        return: pos_vec     -- position as YARP vector
    '''
    pos_vec = yarp.Vector(jnts)

    for j in range(jnts):
        pos_vec.set(j, position[j])

    return pos_vec


def set_pos_vector_same(value, jnts):
    '''
        set position vector with one value for all joints

        params: pos_vec     -- position vector
                value       -- value for all joints, double value
                jnts        -- number of joints

        return: pos_vec     -- position as YARP vector
    '''
    pos_vec = yarp.Vector(jnts)

    for j in range(jnts):
        pos_vec.set(j, value)

    return pos_vec


######################################################################
# Convert between YARP vector and numpy array

def npvec_2_yarpvec(array):
    '''
        convert a 1D numpy array into a YARP vector (double values)

        params: array       -- 1D array-like position vector

        return: yarp_vec    -- YARP vector, result of conversion
    '''
    vector = np.array(array, dtype=np.float64)
    yarp_vec = yarp.Vector(vector.shape[0])

    for i in range(vector.shape[0]):
        yarp_vec.set(i, vector[i])

    return yarp_vec


def yarpvec_2_npvec(yarp_vec):
    '''
        convert a YARP vector into a 1D numpy array

        params: yarp_vec    -- 1D YARP vector

        return: vector      -- 1D Numpy array, result of conversion
    '''
    vector = np.zeros(yarp_vec.length(), dtype=np.float64)

    for i in range(yarp_vec.length()):
        vector[i] = yarp_vec.get(i)

    return vector
