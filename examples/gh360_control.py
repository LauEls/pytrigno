import mujoco
import cv2
import numpy as np

from pytrigno import TrignoCommand, TrignoData
from filter import linear_envelope, ffc_filter

if __name__=="__main__":
    with open('robot_config/gh360.xml', 'r') as f:
        xml = f.read()

    host_ip = "192.168.152.1"
    sid_elbow_pos = 1
    sid_elbow_neg = 2
    emg_max_pos = 2.0
    emg_max_neg = 2.0

    trig_cmd = TrignoCommand(host=host_ip)
    trig_data = TrignoData(sensor_range=(0,3),host=host_ip)

    width = 1920
    height = 1080
    duration = 2.5
    framerate = 60

    # Make model and data
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    # sim = MjSim.from_xml_string(xml)

    i_emg_elbow_pos = sid_elbow_pos - 1
    i_emg_elbow_neg = sid_elbow_neg - 1
    emg_elbow_pos_data = np.zeros(1500)
    emg_elbow_neg_data = np.zeros(1500)

    act_elbow_neg_1 = data.actuator(17)
    act_elbow_pos_1 = data.actuator(18)
    act_elbow_neg_2 = data.actuator(19)
    act_elbow_pos_2 = data.actuator(20)
    
    actuator_2 = data.actuator(23)

    mujoco.mj_resetData(model, data)
    cntr = 0
    # Make renderer, render and show the pixels
    with mujoco.Renderer(model, height, width) as renderer:
        while data.time < duration:
            new_emg_data = trig_data.readEMG()
            new_emg_data_size = len(new_emg_data[i_emg_elbow_pos])
            emg_elbow_pos_data = np.delete(emg_elbow_pos_data,np.linspace(0,new_emg_data_size-1,new_emg_data_size,dtype=int))
            emg_elbow_pos_data = np.concatenate((emg_elbow_pos_data, new_emg_data[i_emg_elbow_pos]), axis=None)
            emg_elbow_neg_data = np.delete(emg_elbow_neg_data,np.linspace(0,new_emg_data_size-1,new_emg_data_size,dtype=int))
            emg_elbow_neg_data = np.concatenate((emg_elbow_neg_data, new_emg_data[i_emg_elbow_neg]), axis=None)

            emg_elbow_pos_data_filtered = ffc_filter(emg_elbow_pos_data,2000,50)
            emg_elbow_pos_data_filtered = linear_envelope(emg_elbow_pos_data_filtered, 2000, 5)
            emg_elbow_neg_data_filtered = ffc_filter(emg_elbow_neg_data,2000,50)
            emg_elbow_neg_data_filtered = linear_envelope(emg_elbow_neg_data_filtered, 2000, 5)

            act_elbow_pos_1.ctrl = emg_elbow_pos_data_filtered[len(emg_elbow_pos_data_filtered)-1]*-360/emg_max_pos
            act_elbow_pos_2.ctrl = emg_elbow_pos_data_filtered[len(emg_elbow_pos_data_filtered)-1]*-360/emg_max_pos
            act_elbow_neg_1.ctrl = emg_elbow_neg_data_filtered[len(emg_elbow_neg_data_filtered)-1]*-360/emg_max_neg
            act_elbow_neg_2.ctrl = emg_elbow_neg_data_filtered[len(emg_elbow_neg_data_filtered)-1]*-360/emg_max_neg
            # act_elbow_pos_2.ctrl = -100.0
            mujoco.mj_step(model, data)
            if cntr < data.time * framerate:
                renderer.update_scene(data, camera='sideview')
                im = renderer.render()
                cv2.imshow('image',im)
                cv2.waitKey(1)
                cntr += 1

        
        
        # im = np.flip(im, axis=0)
        

        