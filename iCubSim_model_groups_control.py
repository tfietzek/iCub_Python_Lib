"""
Created on Thu May 08 20:30:00 2019

@author: Torsten Fietzek

Script to import and control groups of models forming a complex object.
"""

import time
import numpy as np

class ModelGroup:
    """Class for controlling model groups in the iCub simulator."""
    def __init__(self, controller, model_list, mod_type, start_pos, start_orient, model_path):
        """
            Import all models in the model_list, place them at the start position and orientation.

            params:
                controller      -- world controller class for model/object manipulation
                mod_type        -- model type 'model' or 'smodel'; 'smodel' is not affected by gravity
                model_list      -- list containing all used models and textures as tuples
                start_pos       -- start position of the models
                start_orient    -- start orientation of the models
        """
        self._mod_list = []
        self._controller = controller

        controller.set_model_path(model_path)

        for mod in model_list:
            self._mod_list.append(controller.create_model(mod_type, mod[0], mod[1], start_pos))
            time.sleep(0.25)

        self.rotate_model_group(start_orient)

    def move_model_group(self, new_position):
        """
            This method moves the model group to a new position.

            params:
                new_position    -- new position for the model group

            return:
                Returns True/False depending on success failure.
        """
        success = True
        for model in self._mod_list:
            success = success and self._controller.move_model(model, new_position)
            time.sleep(0.25)
        return success

    def get_pos_model_group(self):
        """
            Get the position of the model group.

            return:
                Returns the model group position [x, y, z]; None on failure
        """
        return np.array(self._controller.get_model_location(self._mod_list[0]))


    def rotate_model_group(self, new_orientation):
        """
            Change the orientation of the model group.

            params:
                new_orientation     -- new orientation for the model group

            return:
                Returns True/False depending on success failure.
        """
        success = True
        for model in self._mod_list:
            success = success and self._controller.rotate_model(model, new_orientation)
            time.sleep(0.25)
        return success

    def get_rot_model_group(self):
        """
            Get the model group orientation.

            return:
                Returns the model group orientation [rotx, roty, rotz]; None on failure
            """
        return np.array(self._controller.get_model_orientation(self._mod_list[0]))
