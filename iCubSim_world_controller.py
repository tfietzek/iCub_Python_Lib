"""
    @author: Torsten Fietzek

    Class to control the environment in the iCub simulator, for example simple object manipulation.
    The basis is given for object manipulation in: http://www.icub.org/software_documentation/icub_python_simworld_control.html (Marek Rucinski).
    This is extended with model import/manipulation, get hand position and screen movement.
"""

import collections
import time

import numpy as np
import yarp


yarp.Network.init()
if not yarp.Network.checkNetwork():
    print('[ERROR] Please try running yarp server')


########################################################
class WorldController:
    """Class for controlling iCub simulator via its RPC world port."""

    def __init__(self, robot="icubSim"):
        self._rpc_client = yarp.RpcClient()
        client_wc = "WorldController_" + str(id(self))
        self._port_name = "/" + client_wc + "/commands"
        self._rpc_client.open(self._port_name)
        self._rpc_client.addOutput("/" + robot + "/world")

        # A dictionary to track simulator object IDs for all types of objects
        self._sim_ids_counters = collections.defaultdict(lambda: 0)
        self._sim_mids_counters = collections.defaultdict(lambda: 0)

        # A sequence to track internal object IDs. This list stores tuples (object type, simulator id)
        # so that outside one does not have to remember the type of object.
        self._objects = []
        self._models = []

        self._prepare_scene_cam(client_wc, robot)
        self._screen_on = self._prepare_sim_screen(client_wc, robot)

    def _execute(self, cmd):
        """Execute an RPC command, returning obtained answer bottle."""
        ans = yarp.Bottle()
        self._rpc_client.write(cmd, ans)
        return ans

    def _is_success(self, ans):
        """Check if RPC call answer Bottle indicates successfull execution."""
        return ans.size() == 1 and ans.get(0).asVocab32() == 27503  # Vocab for '[ok]'

    # Prepare data structures and network connection for the iCub simulator world camera
    def _prepare_scene_cam(self, client, robot="icubSim"):
        self._scene_cam = {}

        # Initialization of all needed ports
        # Port for scene image
        self._scene_cam['port'] = yarp.Port()
        if not self._scene_cam['port'].open("/" + client + "/scenecam"):
            print("[ERROR] Could not open scene camera port")
        if not yarp.Network.connect("/" + robot + "/cam", "/" + client + "/scenecam"):
            print("[ERROR] Could not connect input port scene")

        # Initialization of image data structures
        self._scene_cam['np_img'] = np.ones((240, 320, 3), np.uint8)
        self._scene_cam['y_img'] = yarp.ImageRgb()
        self._scene_cam['y_img'].resize(320, 240)

        self._scene_cam['y_img'].setExternal(self._scene_cam['np_img'].data, self._scene_cam['np_img'].shape[1], self._scene_cam['np_img'].shape[0])

    # Prepare connection to the iCub-Simulator screen -> screen need to be enabled in simulator config
    def _prepare_sim_screen(self, client, robot="icubSim"):
        # Port for the screen
        self._output_port_screen = yarp.Port()
        if self._output_port_screen.open(client + "/simscreen"):
            if yarp.Network.connect(client + "/simscreen", "/" + robot + "/texture/screen"):
                return True
            else:
                self._output_port_screen.close()
                print("[ERROR] Could not connect to screen")
                return False
        else:
            print("[ERROR] Could not open screen port")
            return False

########################################################
# Object creation and manipulation
########################################################

    ########################################################
    # Create object inside the simulator
    def _prepare_create_obj_command(self, obj, size, location, color, collision):
        """
            Prepare an RPC command for creating an object in the simulator environment.

            See Simulator Readme section 'Object Creation'

            Parameters:
                obj         -- object type string. 'sph', 'box', 'cyl' 'ssph', 'sbox' or 'scyl'.
                size        -- list of values specifying the size of an object. Parameters depend on object type:
                                (s)box: [ x, y, z ]
                                (s)sph: [ radius ]
                                (s)cyl: [ radius, length ]
                location    -- coordinates of the object location, [ x, y, z ]
                color       -- object colour in RGB (normalised), [ r, g, b ]
                collision   -- activate/deactivate object collision (1/0)

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()

        list(map(result.addString, ["world", "mk", obj]))
        list(map(result.addFloat64, size))
        list(map(result.addFloat64, location))
        list(map(result.addFloat64, color))
        result.addInt32(collision)
        return result

    def create_object(self, obj, size, location, color, collision=1):
        """
            Create an object of a specified type, size, location and colour, returning internal object ID or -1 on error.

            Parameters:
                obj         -- object type string. 'sph' (sphere), 'box' (cuboid), 'cyl'(cylinder), 'ssph', 'sbox' or 'scyl'.
                               With the prefixed "s" the model is unaffected by gravity.
                size        -- list of values specifying the size of an object. Parameters depend on object type:
                                (s)box: [ x, y, z ]
                                (s)sph: [ radius ]
                                (s)cyl: [ radius, length ]
                location    -- coordinates of the object location, [ x, y, z ]
                color       -- object color in RGB (values: [0...1]), [ r, g, b ]
                collision   -- activate/deactivate object collision (1/0)

            Returns:
                internal object ID to reference the object or -1 on error
        """
        cmd = self._prepare_create_obj_command(obj, size, location, color, collision)

        if self._is_success(self._execute(cmd)):
            # iCub simulator IDs start from 1
            obj_sim_id = self._sim_ids_counters[obj] + 1

            # Update the counters

            self._sim_ids_counters[obj] += 1
            self._objects.append((obj, obj_sim_id))

            # Internal object IDs are shared among all types of objects and start from 0;
            # they are essentially indices of the self._objects sequence
            return len(self._objects) - 1

        print('ERROR: Object creation failed!')
        return -1  # error

    ########################################################
    # Move object inside the simulator
    def _prepare_move_command_obj(self, obj, obj_id, location):
        """
            Prepare the "world set <obj> <xyz>" command bottle.

            Parameters:
                obj         -- object descriptor string
                obj_id      -- simulator object ID
                location    -- coordinates of the object location, [ x, y, z ]

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "set", obj]))
        result.addInt32(obj_id)
        list(map(result.addFloat64, location))
        return result

    def move_object(self, obj_id, location):
        """
            Move an object specified by the internal id to another location.

            Parameters:
                obj_id      -- internal model ID to reference the object
                location    -- coordinates of the object location, [ x, y, z ]

            Returns:
                True/False dependent on success/failure.
        """
        obj_desc = self._objects[obj_id]
        return self._is_success(self._execute(self._prepare_move_command_obj(obj_desc[0], obj_desc[1], location)))

    ########################################################
    # Get object position inside the simulator
    def _prepare_get_pos_command_obj(self, obj, obj_id):
        """
            Prepare the "world get <obj> <id>" command bottle.

            Parameters:
                obj         -- object descriptor string
                obj_id      -- simulator object ID

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", obj]))
        result.addInt32(obj_id)
        return result

    def get_object_location(self, obj_id):
        """
            Obtain the object location from the simulator.

            Parameters:
                obj_id      -- internal object ID

            Returns:
                object location coordinates [x, y, z]; None on failure.

        """
        obj_desc = self._objects[obj_id]
        result = self._execute(
            self._prepare_get_pos_command_obj(obj_desc[0], obj_desc[1]))
        if result.size() == 3:
            # 3-element list with xyz coordinates
            return np.array([result.get(i).asDouble() for i in range(3)])

        return None  # An error occured

    ########################################################
    # Rotate object inside the simulator
    def _prepare_rot_command_obj(self, obj, obj_id, orientation):
        """
            Prepare the "world rot <obj> <id> <xyz>" command bottle.

            Parameters:
                obj         -- object descriptor string
                obj_id      -- simulator object ID
                orientation -- new object orientation [rotx, roty, rotz]

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "rot", obj]))
        result.addInt32(obj_id)
        list(map(result.addFloat64, orientation))
        return result

    def rotate_object(self, obj_id, orientation):
        """
            Move an object specified by the internal id to another location.

            Parameters:
                obj_id      -- internal object ID
                orientation -- new object orientation [rotx, roty, rotz]

            Returns:
                True/False dependent on success/failure.
        """
        obj_desc = self._objects[obj_id]
        return self._is_success(self._execute(self._prepare_rot_command_obj(obj_desc[0], obj_desc[1], orientation)))

    ########################################################
    # Get object orientation inside the simulator
    def _prepare_get_rot_command_obj(self, obj, obj_id):
        """
            Prepare the "world rot <obj> <id>" command bottle.

            Parameters:
                obj         -- object descriptor string
                obj_id      -- simulator object ID

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "rot", obj]))
        result.addInt32(obj_id)
        return result

    def get_object_orientation(self, obj_id):
        """
            Obtain the object location from the simulator.

            Parameters:
                obj_id      -- internal object ID

            Returns:
                object orientation [rotx, roty, rotz]; None on failure
        """
        obj_desc = self._objects[obj_id]
        result = self._execute(
            self._prepare_get_rot_command_obj(obj_desc[0], obj_desc[1]))
        if result.size() == 3:
            # 3-element list with xyz angles
            return np.array([result.get(i).asDouble() for i in range(3)])

        return None  # An error occured

########################################################
# 3D-Model creation and manipulation
########################################################

    ########################################################
    # Load 3D model into the simulator
    def _prepare_create_command_model(self, m_type, model, texture, location):
        """
            Prepare an RPC command for importing a model in the simulator environment.

            Parameters:
                m_type      -- model type as string: 'smodel', 'model'
                model       -- model file name, for example 'model.x' (only type .x)
                texture     -- texture file name, for example 'gruen.bmp' (only type .bmp)
                location    -- coordinates of the model location, [ x, y, z ]

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "mk", m_type, model, texture]))
        list(map(result.addFloat64, location))
        return result

    def create_model(self, m_type, model, texture, location):
        """
            Import a model of a specified type, texture and location.

            For further details see Simulator Readme section 'Importing 3D models into the simulator'

            Parameters:
                m_type      -- model type as string: 'smodel', 'model'
                model       -- model file name, for example 'model.x' (only type .x)
                texture     -- texture file name, for example 'gruen.bmp' (only type .bmp)
                location    -- coordinates of the model location, [ x, y, z ]

            Returns:
                internal model ID to reference the model or -1 on error
        """
        cmd = self._prepare_create_command_model(
            m_type, model, texture, location)
        if self._is_success(self._execute(cmd)):
            # iCub simulator IDs start from 1
            mod_sim_id = self._sim_mids_counters[m_type] + 1

            # Update the counters
            self._sim_mids_counters[m_type] += 1
            self._models.append((m_type, mod_sim_id))

            # Internal model IDs are shared among all models and start from 0;
            # they are essentially indices of the self._models sequence
            return len(self._models) - 1

        print("ERROR: Model import failed!")
        return -1  # error

    ########################################################
    # Move model inside the simulator
    def _prepare_move_command_model(self, m_type, mod_id, location):
        """
            Prepare the "world set <mod> <xyz>" command bottle.

            Parameters:
                m_type      -- model type as string: 'smodel', 'model'
                mod_id      -- simulator model ID
                location    -- coordinates of the model location, [ x, y, z ]
            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "set", m_type]))
        result.addInt32(mod_id)
        list(map(result.addFloat64, location))
        return result

    def move_model(self, mod_id, location):
        """
            Move a model specified by the internal id to another location.

            Parameters:
                mod_id      -- internal model ID
                location    -- coordinates of the model location, [ x, y, z ]

            Returns:
                True/False dependent on success/failure.
        """
        mod_desc = self._models[mod_id]
        return self._is_success(self._execute(self._prepare_move_command_model(mod_desc[0], mod_desc[1], location)))

    ########################################################
    # Get model position inside the simulator
    def _prepare_get_pos_command_model(self, m_type, mod_id):
        """
            Prepare the "world get <mod> <id>" command bottle.

            Parameters:
                m_type      -- model type as string: 'smodel', 'model'
                mod_id      -- simulator model ID

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", m_type]))
        result.addInt32(mod_id)
        return result

    def get_model_location(self, mod_id):
        """
            Obtain the model location from the simulator.

            Parameters:
                mod_id      -- internal model ID

            Returns:
                model location coordinates [x, y, z]; None on failure.
        """
        mod_desc = self._models[mod_id]
        result = self._execute(
            self._prepare_get_pos_command_model(mod_desc[0], mod_desc[1]))
        if result.size() == 3:
            # 3-element list with xyz coordinates
            return np.array([result.get(i).asDouble() for i in range(3)])

        return None  # An error occured

    ########################################################
    # Rotate model inside the simulator
    def _prepare_rot_command_model(self, m_type, mod_id, orientation):
        """
            Prepare the "world rot <mod> <rotx roty rotz>" command bottle.

            Parameters:
                m_type      -- model type as string: 'smodel', 'model'
                mod_id      -- simulator model ID
                orientation -- new model orientation [rotx, roty, rotz]

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "rot", m_type]))
        result.addInt32(mod_id)
        list(map(result.addFloat64, orientation))
        return result

    def rotate_model(self, mod_id, orientation):
        """
            Move a model specified by the internal id to another location.

            Parameters:
                mod_id      -- internal model ID
                orientation -- new model orientation [rotx, roty, rotz]

            Returns:
                True/False dependent on success/failure.
        """
        mod_desc = self._models[mod_id]
        return self._is_success(self._execute(self._prepare_rot_command_model(mod_desc[0], mod_desc[1], orientation)))

    ########################################################
    # Get model orientation inside the simulator
    def _prepare_get_rot_command_model(self, m_type, mod_id):
        """
            Prepare the "world rot <mod> <id>" command bottle.

            Parameters:
                m_type      -- model type as string: 'smodel', 'model'
                mod_id      -- simulator model ID

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "rot", m_type]))
        result.addInt32(mod_id)
        return result

    def get_model_orientation(self, mod_id):
        """
            Obtain the model rotation from the simulator.

            Parameters:
                mod_id      -- internal model ID

            Returns:
                model orientation [rotx, roty, rotz]; None on failure
        """
        mod_desc = self._models[mod_id]
        result = self._execute(
            self._prepare_get_rot_command_model(mod_desc[0], mod_desc[1]))
        if result.size() == 3:
            # 3-element list with xyz angles
            return np.array([result.get(i).asDouble() for i in range(3)])

        return None  # An error occured

    ########################################################
    # Get path to model and texture files
    def _prepare_get_path_command_model(self):
        """
            Prepare the "world get mdir" command bottle.

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", "mdir"]))
        return result

    def get_model_path(self):
        """
            Obtain the path to model and texture files.

            Returns:
                Absolute path to model and texture files set in the simulator. Returns None on failure.
        """
        result = self._execute(self._prepare_get_path_command_model())
        if result.size() == 1:
            return result.get(0).asString()  # path to model and texture files

        return None  # An error occured

    ########################################################
    # Set path to model and texture files
    def _prepare_set_path_command_model(self, path):
        """
            Prepare the "world set mdir" command bottle.

            Parameters:
                path      -- New absolute path to model and texture files.

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "set", "mdir", path]))
        return result

    def set_model_path(self, path):
        """
            Set the path to model and texture files.

            Parameters:
                path      -- New absolute path to model and texture files.

            Returns:
                True/False dependent on success/failure.
        """
        return self._is_success(self._execute(self._prepare_set_path_command_model(path)))

########################################################
# special commands
########################################################

    ########################################################
    # Get hand position
    def _prepare_get_command_hand(self, hand):
        """
            Prepare the "world get <hand>" command bottle.

            Parameters:
                hand      -- string 'lhand' or 'rhand', defines the which hand is choosen

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", hand]))
        return result

    def get_hand_location(self, hand):
        """
            Obtain the hand location from the simulator.

            Parameters:
                hand      -- string 'lhand' or 'rhand', defines the which hand is choosen

            Returns:
                hand location coordinates [x, y, z]; None on failure
        """
        result = self._execute(self._prepare_get_command_hand(hand))
        if result.size() == 3:
            # 3-element list with xyz coordinates
            return np.array([result.get(i).asDouble() for i in range(3)])

        return None  # An error occured

    ########################################################
    # Get screen position
    def _prepare_get_command_screen(self):
        """
            Prepare the "world get screen" command bottle.

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "get", "screen"]))
        return result

    def get_screen_location(self):
        """
            Obtain the screen location from the simulator.

            Returns:
                screen location coordinates [x, y, z]; None on failure
        """
        result = self._execute(self._prepare_get_command_screen())
        if result.size() == 3:
            # 3-element list with xyz coordinates
            return np.array([result.get(i).asDouble() for i in range(3)])

        return None  # An error occured

    ########################################################
    # Set screen position
    def _prepare_set_command_screen(self, location):
        """
            Prepare the "world set screen <location>" command bottle.

            Parameter:
                location        --screen location coordinates [x, y, z]

            Returns:
                yarp.Bottle with the command, ready to be sent to the rpc port of the simulator
        """
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "set", "screen"]))
        list(map(result.addFloat64, location))
        return result

    def set_screen_location(self, location):
        """
            Set the screen inside simulator to a new position.

            Parameter:
                location        -- new screen location coordinates [x, y, z]

            Returns:
                True/False dependent on success/failure.
        """
        return self._is_success(self._execute(self._prepare_set_command_screen(location)))

    ########################################################
    # Write image to simulator screen
    def set_screen_image(self, image):
        """
        Show image on the screen in the iCub-simulator.

        Parameters
        ----------
        image : NDarray/YARP-Image
            image to be shown on the screen
        """
        if isinstance(image, yarp.Image):
            out = self._output_port_screen.write(image)
            time.sleep(0.03)
            return out
        else:
            eye_img_array = np.array(image)
            if len(eye_img_array.shape) == 2 or (len(eye_img_array.shape) == 3 and eye_img_array.shape[2] == 1):
                eye_img_array = np.reshape(eye_img_array, (eye_img_array.shape[0], eye_img_array.shape[1]))
                eye_yarp_image = yarp.ImageFloat()

            elif len(eye_img_array.shape) == 3 and eye_img_array.shape[2] == 3:
                eye_yarp_image = yarp.ImageRgb()

            else:
                print("[Error] Not a compatible image size!")
                return False

            eye_yarp_image.resize(eye_img_array.shape[1], eye_img_array.shape[0])
            eye_yarp_image.setExternal(eye_img_array.data, eye_img_array.shape[1], eye_img_array.shape[0])
            out = self._output_port_screen.write(eye_yarp_image)
            time.sleep(0.03)
            return out

    ########################################################
    # Read image from simulator world camera
    def get_world_image(self):
        """
        Retrieve image from the world camera in the iCub-simulator.

        Returns
        -------
        NDarray
            return image from the world camera
        """
        self._scene_cam['port'].read(self._scene_cam['y_img'])
        self._scene_cam['port'].read(self._scene_cam['y_img'])

        if self._scene_cam['y_img'].getRawImage().__int__() != self._scene_cam['np_img'].__array_interface__['data'][0]:
            print("read() reallocated my self._scene_cam['y_img']!")

        return self._scene_cam['np_img'].copy()

    ########################################################
    # Delete all objects and models from simulator world
    def _prepare_del_all_command(self):
        """Prepare the "world del all" command bottle."""
        result = yarp.Bottle()
        result.clear()
        list(map(result.addString, ["world", "del", "all"]))
        return result

    def del_all(self):
        """Delete all objects and models from the simulator"""
        result = self._is_success(self._execute(
            self._prepare_del_all_command()))

        if result:
            # Clear the counters
            self._sim_ids_counters.clear()
            self._sim_mids_counters.clear()
            del self._objects[:]
            del self._models[:]
        return result

########################################################
# call destructor
    def __del__(self):
        try:
            if self._rpc_client is not None:
                self.del_all()
            self._rpc_client.close()
            del self._rpc_client
            if self._screen_on:
                self._output_port_screen.close()
            self._scene_cam['port'].close()

        except AttributeError:
            pass
