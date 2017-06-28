#!/usr/bin/python

### import guacamole libraries ###
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.daemon

from .GestureRecognizer import *
from .GestureParser import *
import lib.Utility
from scipy import misc

    


class RayPointer(avango.script.Script):

    ## input fields
    sf_button_down = avango.SFBool()
    sf_button_up = avango.SFBool()


    ## constructor
    def __init__(self):
        self.super(RayPointer).__init__()

        # pointer movement list
        self.pointer_movement = []
        self.initial_direction = None
        self.is_dragging = None
        self.p_is_moving = False
        self.proxy_list = []
        self.gesture_vector_list = []
        self.gesture_id = 0


    def my_constructor(self,
        SCENEGRAPH = None,
        PARENT_NODE = None,
        POINTER_TRACKING_STATION = None,
        TRACKING_TRANSMITTER_OFFSET = avango.gua.make_identity_mat(),
        POINTER_DEVICE_STATION = None,
        ):


        ### external references ###
        self.SCENEGRAPH = SCENEGRAPH


        ### parameters ###
        
        ## visualization
        self.ray_length = 2.0 # in meter
        self.ray_thickness = 0.0075 # in meter

        self.intersection_point_size = 0.01 # in meter

        ## picking
        self.white_list = []   
        self.black_list = ["invisible"]

        self.pick_options = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
                            | avango.gua.PickingOptions.GET_POSITIONS \
                            | avango.gua.PickingOptions.GET_NORMALS \
                            | avango.gua.PickingOptions.GET_WORLD_POSITIONS \
                            | avango.gua.PickingOptions.GET_WORLD_NORMALS


        ### resources ###


        ### init recognizer and detection
        self.recognizer = GestureRecognizer()
        # self.parser = GestureParser(SCALE_MODE=ScaleMode.NO_SCALE, IMAGE_DIMENSION=32)
        self.parser = GestureParser(SCALE_MODE=ScaleMode.SCALE_MAX, IMAGE_DIMENSION=32)

        self.gesture_dataset, self.gesture_targets = lib.Utility.load_datasets("gestures/", 4)
        self.recognizer.initialize(self.gesture_dataset)
        self.checkifsame = None
    


        ## init sensors
        self.pointer_tracking_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.pointer_tracking_sensor.Station.value = POINTER_TRACKING_STATION
        self.pointer_tracking_sensor.TransmitterOffset.value = TRACKING_TRANSMITTER_OFFSET
            
        self.pointer_device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.pointer_device_sensor.Station.value = POINTER_DEVICE_STATION

        self.sf_button_down.connect_from(self.pointer_device_sensor.Button0)
        self.sf_button_up.connect_from(self.pointer_device_sensor.Button1)


        ## init nodes

        self.pointer_node = avango.gua.nodes.TransformNode(Name = "pointer_node")
        self.pointer_node.Transform.connect_from(self.pointer_tracking_sensor.Matrix)
        PARENT_NODE.Children.value.append(self.pointer_node)


        _loader = avango.gua.nodes.TriMeshLoader()

        self.ray_geometry = _loader.create_geometry_from_file("ray_geometry", "data/objects/cylinder.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.ray_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.0,0.0,self.ray_length * -0.5) * \
            avango.gua.make_rot_mat(-90.0,1,0,0) * \
            avango.gua.make_scale_mat(self.ray_thickness, self.ray_length, self.ray_thickness)
        self.ray_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0,0.0,0.0,1.0))
        self.pointer_node.Children.value.append(self.ray_geometry)


        self.intersection_geometry = _loader.create_geometry_from_file("intersection_geometry", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.intersection_geometry.Tags.value = ["invisible"] # set geometry invisible
        self.intersection_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0,0.0,0.0,1.0))
        self.SCENEGRAPH.Root.value.Children.value.append(self.intersection_geometry)


        self.ray = avango.gua.nodes.Ray()    
      
        self.always_evaluate(True) # change global evaluation policy


      
        
    
    ### functions ###

    def calc_pick_result(self, PICK_MAT = avango.gua.make_identity_mat()):

        # update ray parameters
        self.ray.Origin.value = PICK_MAT.get_translate()

        _vec = avango.gua.make_rot_mat(PICK_MAT.get_rotate_scale_corrected()) * avango.gua.Vec3(0.0,0.0,-1.0)
        _vec = avango.gua.Vec3(_vec.x,_vec.y,_vec.z)

        self.ray.Direction.value = _vec * self.ray_length

        # intersect
        _mf_pick_result = self.SCENEGRAPH.ray_test(self.ray, self.pick_options, self.white_list, self.black_list)
        return _mf_pick_result


    def update_ray_visualization(self, PICK_WORLD_POS = None, PICK_DISTANCE = 0.0):

        if PICK_WORLD_POS is None: # nothing hit
            self.ray_geometry.Transform.value = \
                avango.gua.make_trans_mat(0.0,0.0,self.ray_length * -0.5) * \
                avango.gua.make_rot_mat(-90.0,1,0,0) * \
                avango.gua.make_scale_mat(self.ray_thickness, self.ray_length, self.ray_thickness)
        
            self.intersection_geometry.Tags.value = ["invisible"] # set intersection point invisible

        else: # something hit
            self.ray_geometry.Transform.value = \
                avango.gua.make_trans_mat(0.0,0.0,PICK_DISTANCE * -0.5) * \
                avango.gua.make_rot_mat(-90.0,1,0,0) * \
                avango.gua.make_scale_mat(self.ray_thickness, PICK_DISTANCE, self.ray_thickness)

            self.intersection_geometry.Tags.value = [] # set intersection point invisible

            self.intersection_geometry.Transform.value = avango.gua.make_trans_mat(PICK_WORLD_POS) * avango.gua.make_scale_mat(self.intersection_point_size)

    def convert_point_list_to_qimage(self, image_array):
        width = image_array.shape[0]
        height = image_array.shape[1]
        black = QtGui.QColor(0, 0, 0).rgb()
        white = QtGui.QColor(255, 255, 255).rgb()
        img = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
        for r in range(width):
            for c in range(height):

                if image_array[r, c] == 255:
                    img.setPixel(c, r, white)
                else:
                    img.setPixel(c, r, black)
        return img

    def start_dragging(self):          
        print("start dragging called")

        # clear last gesture point array
        # del self.pointer_movement[:]

        # save starting direction
        # self.initial_direction = self.ray.Direction.value
        # print(self.initial_direction)

        # start dragging
        self.is_dragging = True;

  
    def stop_dragging(self): 
        pass

        # stop dragging
        # self.is_dragging = False;

        # print number of captured elements in gestrure array
        # print("number of detected pointer position elements: %i" % len(self.pointer_movement))

    def dragging(self):
        # if the pointer is dragged save pointer world pos in array
        if self.is_dragging:
            pass


    def start_gesture(self):          
        print("start gesture")

        # clear last gesture point array
        del self.pointer_movement[:]

        for proxy in self.proxy_list:
            self.SCENEGRAPH.Root.value.Children.value.remove(proxy)

        del self.proxy_list[:]

        # save starting direction
        self.initial_direction = self.ray.Direction.value
        print(self.initial_direction)

        # start dragging
        self.p_is_moving = True;

  
    def end_gesture(self): 

        # stop dragging
        self.p_is_moving = False;

        # print number of captured elements in gestrure array
        # print("number of detected pointer position elements: %i" % len(self.pointer_movement))
        if len(self.gesture_vector_list) > 2:
            # print(self.gesture_vector_list)
            # self.recognize_gesture_2d()
            #self.write_gesture_symbol(self.gesture_id)
            self.recognize_gesture_3d()
            # self.write_gesture_symbol(self.gesture_id)
            self.gesture_id += 1
            del self.gesture_vector_list[:]

            print("end gesture")


    def recognize_gesture_2d(self):
        point_list = [Point(p[0], p[1]) for p in self.gesture_vector_list]
        image_array = self.parser.convert_point_list_to_scaled_image_array(point_list)
        grey_array = lib.Utility.ndarray_color_to_grey(image_array)

        new_size = (16, 16)
        _grey_img_scaled = misc.imresize(grey_array, new_size) / 16

        _grey_img_array = _grey_img_scaled.flatten()

        result = self.recognizer.predict([_grey_img_array])
        print(result)


    def recognize_gesture_3d(self):
        points = lib.Utility.prepare_gvl_for_plane_detection(self.gesture_vector_list)
        two_dim_points = lib.Utility.project_3d_points_to_2d_space(points)

        self.write_gpl_file(self.gesture_id, two_dim_points)
        # 
        point_list = [Point(p[0], p[1]) for p in two_dim_points]

        image_array = self.parser.convert_point_list_to_scaled_image_array(point_list)

        #print("img",image_array)
        
        # grey_array = lib.Utility.ndarray_color_to_grey(image_array)

        #for row in grey_array:
        #    print("grey image row", row)
        #print("grey", grey_array)

        new_size = (16, 16)
        _grey_img_scaled = misc.imresize(image_array, new_size) / 16

        _grey_img_array = _grey_img_scaled.flatten()
        # print(_grey_img_array)
        if self.checkifsame is not None:
            if (self.checkifsame == _grey_img_array).all:
                print("oh no this is tha same")
            else:
                print("errror is not here")
            self.checkifsame = _grey_img_array
        else:
            self.checkifsame = _grey_img_array

        result = self.recognizer.predict([_grey_img_array])
        print(result)


    def write_gesture_symbol(self, id):
        if len(self.gesture_vector_list) > 3:
            file = open('test_gestures/gesture_'+str(id)+".gpl", "w")
            for point in self.gesture_vector_list:
                # file.write(str(point)+"\n")
                file.write( str(point[0]) + " " + str(point[1]) + " " + str(point[2])  + "\n")
                #file.write( str(point[0]) + " " + str(point[1]) + "\n")

            file.close()

    def write_gpl_file(self, id, point_list):
        #print(point_list)
        if len(point_list) > 3:
            file = open('gesture_point_lists/gesture_'+str(id)+".gpl", "w")
            for point in point_list:
                #print("Point" , point)
                # file.write(str(point)+"\n")
                file.write( str(point[0]) + " " + str(point[1])+ "\n")
                #file.write( str(point[0]) + " " + str(point[1]) + "\n")

            file.close()

    def moving_pointer_2d(self):
            
        # init nodes and geometries
        _loader = avango.gua.nodes.TriMeshLoader() 
        
        if self.p_is_moving:
            a = self.calc_pick_result(self.pointer_node.WorldTransform.value)
            if len(a.value) > 0:
                _picked_object = a.value[0]
                #_pick_rot = _picked_object.Rotation.value
                #print(_pick_rot)
                _pick_pos = _picked_object.WorldPosition.value
                print(_pick_pos)
                self.gesture_vector_list.append(_pick_pos)
                _pick_mat = avango.gua.make_trans_mat(_pick_pos)

                _proxy = _loader.create_geometry_from_file("proxy_geo", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)
                _proxy.Transform.value = _pick_mat * avango.gua.make_scale_mat(0.02)
                _proxy.Material.value.set_uniform("Color", avango.gua.Vec4(0.0, 0.5, 1.0, 1.0))
                self.proxy_list.append(_proxy)
                self.SCENEGRAPH.Root.value.Children.value.append(_proxy)
        
    def moving_pointer_3d(self):

        # init nodes and geometries
        _loader = avango.gua.nodes.TriMeshLoader() 
        if self.p_is_moving:
            a = self.pointer_node.WorldTransform.value

            _pick_pos = a.get_translate()
            self.gesture_vector_list.append(_pick_pos)
            #_pick_mat = _pick_pos
            _pick_mat = avango.gua.make_trans_mat(_pick_pos)

            _proxy = _loader.create_geometry_from_file("proxy_geo", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)
            _proxy.Transform.value = _pick_mat * avango.gua.make_scale_mat(0.02)
            _proxy.Material.value.set_uniform("Color", avango.gua.Vec4(0.0, 0.5, 1.0, 1.0))
            self.proxy_list.append(_proxy)
            self.SCENEGRAPH.Root.value.Children.value.append(_proxy)


    ### callback functions ###
    @field_has_changed(sf_button_down)
    def sf_button_down_changed(self):

        if self.sf_button_down.value == True: # button pressed

            # _mf_pick_result = self.calc_pick_result(PICK_MAT = self.pointer_node.WorldTransform.value)
    
            # if len(_mf_pick_result.value) > 0: # intersection found
            #     _pick_result = _mf_pick_result.value[0] # get first pick result

            #     _node = _pick_result.Object.value # get intersected geometry node
            #     #_node = _node.Parent.value # take the parent node of the geomtry node (the whole car)

            #     self.start_dragging(_node)

            self.start_dragging()

        else: # button released
            self.stop_dragging()



    ### callback functions ###
    @field_has_changed(sf_button_up)
    def sf_button_up_changed(self):

        if self.sf_button_up.value == True: # button pressed
            self.start_gesture()
            
        else: # button released
            self.end_gesture()
            


    
    def evaluate(self):   
        ## calc ray intersection
        _mf_pick_result = self.calc_pick_result(PICK_MAT = self.pointer_node.WorldTransform.value)

        #print("hits:", len(_mf_pick_result.value))
    
        if len(_mf_pick_result.value) > 0: # intersection found
            _pick_result = _mf_pick_result.value[0] # get first pick result

            _node = _pick_result.Object.value # get intersected geometry node
    
            _pick_pos = _pick_result.Position.value # pick position in object coordinate system
            _pick_world_pos = _pick_result.WorldPosition.value # pick position in world coordinate system
    
            _distance = _pick_result.Distance.value * self.ray_length # pick distance in ray coordinate system
    
            # print(_node, _pick_pos, _pick_world_pos, _distance)

            self.update_ray_visualization(PICK_WORLD_POS = _pick_world_pos, PICK_DISTANCE = _distance)
    
        else: # nothing hit
            self.update_ray_visualization() # apply default ray visualization
        


        # self.dragging() # possibly drag object
        # self.moving_pointer_2d()
        self.moving_pointer_3d()

"""
        # init nodes and geometries
        _loader = avango.gua.nodes.TriMeshLoader() 
        
        if self.p_is_moving:
            a = self.calc_pick_result(self.pointer_node.WorldTransform.value)
            if len(a.value) > 0:
                _picked_object = a.value[0]
                _pick_pos = _picked_object.Position.value
                self.gesture_vector_list.append(_pick_pos)
                _pick_mat = avango.gua.make_trans_mat(_pick_pos)

                _proxy = _loader.create_geometry_from_file("proxy_geo", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)
                _proxy.Transform.value = _pick_mat * avango.gua.make_scale_mat(0.02)
                _proxy.Material.value.set_uniform("Color", avango.gua.Vec4(0.0, 0.5, 1.0, 1.0))
                self.proxy_list.append(_proxy)
                self.SCENEGRAPH.Root.value.Children.value.append(_proxy)
"""