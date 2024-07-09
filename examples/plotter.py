import matplotlib.pyplot as plt
import numpy as np
import argparse

from pytrigno import TrignoCommand, TrignoData
from filter import linear_envelope, ffc_filter

if __name__=="__main__":
    host_ip = "192.168.152.1"
    sensor_id = 1
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-h", "--host", default="192.168.152.1", type=str)
    # parser.add_argument("-s", "--sensor_id", default=1, type=int)
    # args = parser.parse_args()

    trig_cmd = TrignoCommand(host=host_ip)
    trig_data = TrignoData(sensor_range=(0,3),host=host_ip)

    emg_data_buffer_size = 20000
    acc_data_buffer_size = 2000
    gyro_data_buffer_size = 2000

    emg_data = np.zeros(emg_data_buffer_size)
    emg_le_data = np.zeros(emg_data_buffer_size)
    emg_ffc_le_data = np.zeros(emg_data_buffer_size)
    emg_x_axis = np.linspace(1,emg_data_buffer_size,emg_data_buffer_size)
    acc_data = np.zeros((3,acc_data_buffer_size))
    acc_x_axis = np.linspace(1,acc_data_buffer_size,acc_data_buffer_size)
    gyro_data = np.zeros((3,gyro_data_buffer_size))
    gyro_x_axis = np.linspace(1,gyro_data_buffer_size,gyro_data_buffer_size)

    plt.ion()
    figure, (ax_emg,ax_acc,ax_gyro) = plt.subplots(3,1,figsize=(10*3,8*3))
    #TRY ADDING A FIGURE TITLE THAT SHOWS WHICH SENSOR IS PLOTTED!!!!!!!!!!!!!
    line_emg, = ax_emg.plot(emg_x_axis, emg_data, label='emg raw')
    line_emg_le, = ax_emg.plot(emg_x_axis, emg_le_data, label='emg le filter')
    line_emg_ffc_le, = ax_emg.plot(emg_x_axis, emg_ffc_le_data, label='emg ffc+le filter')
    ax_emg.set_ylim(-4, 4)
    ax_emg.set_title("EMG Sensor "+str(sensor_id))
    ax_emg.set_xlabel("sample in buffer")
    ax_emg.set_ylabel("muscle activity [mV]")
    emg_leg = ax_emg.legend(loc="upper right")
    line_acc_x, = ax_acc.plot(acc_x_axis, acc_data[0], label='x')
    line_acc_y, = ax_acc.plot(acc_x_axis, acc_data[1], label='y')
    line_acc_z, = ax_acc.plot(acc_x_axis, acc_data[2], label='z')
    ax_acc.set_ylim(-2, 2)
    ax_acc.set_title("Accelerometer")
    ax_acc.set_xlabel("sample in buffer")
    ax_acc.set_ylabel("acceleration/9.8 [ms^2]")
    acc_leg = ax_acc.legend(loc="upper right")
    line_gyro_x, = ax_gyro.plot(gyro_x_axis, gyro_data[0], label='x')
    line_gyro_y, = ax_gyro.plot(gyro_x_axis, gyro_data[1], label='y')
    line_gyro_z, = ax_gyro.plot(gyro_x_axis, gyro_data[2], label='z')
    ax_gyro.set_ylim(-200, 200)
    ax_gyro.set_title("Gyroscope")
    ax_gyro.set_xlabel("sample in buffer")
    ax_gyro.set_ylabel("angular velocity [deg/s]")
    gyro_leg = ax_gyro.legend(loc="upper right")

    trig_cmd.start()
    i_emg = sensor_id -1
    i_acc = ((sensor_id-1)*9, (sensor_id-1)*9+3)
    i_gyro = ((sensor_id-1)*9+3, (sensor_id-1)*9+6)

    for i in range(1000):
        new_emg_data = trig_data.readEMG()
        new_imu_data = trig_data.readIMU()

        new_emg_data_size = len(new_emg_data[i_emg])
        new_acc_data_size = len(new_imu_data[i_acc[0]])
        new_gyro_data_size = len(new_imu_data[i_gyro[0]])
        emg_data = np.delete(emg_data,np.linspace(0,new_emg_data_size-1,new_emg_data_size,dtype=int))
        acc_data = np.delete(acc_data,np.linspace(0,new_acc_data_size-1,new_acc_data_size,dtype=int),1)
        gyro_data = np.delete(gyro_data,np.linspace(0,new_gyro_data_size-1,new_gyro_data_size,dtype=int),1)

        emg_data = np.concatenate((emg_data, new_emg_data[i_emg]), axis=None)
        acc_data = np.concatenate((acc_data, new_imu_data[i_acc[0]:i_acc[1]]), axis=1)
        gyro_data = np.concatenate((gyro_data, new_imu_data[i_gyro[0]:i_gyro[1]]), axis=1)
        emg_le_data = linear_envelope(emg_data, 2000, 5)
        emg_ffc_le_data = ffc_filter(emg_data,2000,50)
        emg_ffc_le_data = linear_envelope(emg_ffc_le_data, 2000, 5)

        line_emg.set_ydata(emg_data)
        line_emg_le.set_ydata(emg_le_data)
        line_emg_ffc_le.set_ydata(emg_ffc_le_data)
        line_acc_x.set_ydata(acc_data[0])
        line_acc_y.set_ydata(acc_data[1])
        line_acc_z.set_ydata(acc_data[2])
        line_gyro_x.set_ydata(gyro_data[0])
        line_gyro_y.set_ydata(gyro_data[1])
        line_gyro_z.set_ydata(gyro_data[2])

        figure.canvas.draw()
        figure.canvas.flush_events()

    trig_cmd.stop()