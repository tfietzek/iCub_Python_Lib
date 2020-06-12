"""
    Created on Thu May 02 03:55:00 2019

    @author: Torsten Follak

    This file set up the dictionaries for the model groups, containing model and texture names, model type, start position and orientation.
    The created models are a toy car, a simple pencil and a toy bear.
"""

import os

model_path = os.path.abspath("../../iCub_simulator_tools/iCubSim_environment/new_models")

################################################################
############### model description for simple pen ###############
path_pen = model_path + "/pen"
model_list_pen = []

model_list_pen.append(("pen_simple_pen_small.x", "orange.bmp"))
model_list_pen.append(("pen_simple_tip_small.x", "black.bmp"))

dictionary_pen = {'model_type': 'smodel', 'model_list': model_list_pen, 'start_pos': [0.0, 0.0, 1.0],
                  'start_orient': [0.0, 0.0, 0.0], 'model_path': path_pen}


################################################################
############### model description for simple car ###############
path_car = model_path + "/car"

model_list_car = []

model_list_car.append(("car_windows_small.x", "grey.bmp"))

#model_list_car.append(("car_window_0.x", "grey.bmp"))
#model_list_car.append(("car_window_1.x", "grey.bmp"))
#model_list_car.append(("car_window_2.x", "grey.bmp"))
#model_list_car.append(("car_window_3.x", "grey.bmp"))

model_list_car.append(("car_wheels_small.x", "black.bmp"))

#model_list_car.append(("car_wheel_0.x", "black.bmp"))
#model_list_car.append(("car_wheel_1.x", "black.bmp"))
#model_list_car.append(("car_wheel_2.x", "black.bmp"))
#model_list_car.append(("car_wheel_3.x", "black.bmp"))

model_list_car.append(("car_light_0_small.x", "red.bmp"))
model_list_car.append(("car_light_1_small.x", "red.bmp"))

model_list_car.append(("car_light_2_small.x", "yellow.bmp"))
model_list_car.append(("car_light_3_small.x", "yellow.bmp"))

model_list_car.append(("car_body_small.x", "blue.bmp"))

dictionary_car = {'model_type': "smodel", 'model_list': model_list_car, 'start_pos': [0.0, 0.0, 1.0],
                  'start_orient': [0.0, 0.0, 0.0], 'model_path': path_car}


################################################################
################ model description for toy bear ################
path_bear = model_path + "/bear"

model_list_bear = []

model_list_bear.append(("bear_inlet_leg_0_small.x", "beige.bmp"))
model_list_bear.append(("bear_inlet_leg_1_small.x", "beige.bmp"))
model_list_bear.append(("bear_inlet_arm_0_small.x", "beige.bmp"))
model_list_bear.append(("bear_inlet_arm_1_small.x", "beige.bmp"))
model_list_bear.append(("bear_inlet_ear_0_small.x", "beige.bmp"))
model_list_bear.append(("bear_inlet_ear_1_small.x", "beige.bmp"))

model_list_bear.append(("bear_eye_0_small.x", "black.bmp"))
model_list_bear.append(("bear_eye_1_small.x", "black.bmp"))
model_list_bear.append(("bear_nose_small.x", "black.bmp"))

model_list_bear.append(("bear_body_small.x", "brown.bmp"))

dictionary_bear = {'model_type': "smodel", 'model_list': model_list_bear, 'start_pos': [0.0, 0.0, 1.0],
                   'start_orient': [0.0, 0.0, 0.0], 'model_path': path_bear}
