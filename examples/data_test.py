from pytrigno_test import TrignoAccel, TrignoEMG
import matplotlib.pyplot as plt
import numpy as np
import math
import time


def plotIMUdata():
    x_acc = np.zeros(20)
    y_acc = np.zeros(20)
    z_acc = np.zeros(20)
    x_gyro = np.zeros(20)
    y_gyro = np.zeros(20)
    z_gyro = np.zeros(20)
    t = np.linspace(1,20,20)

    trig_imu=TrignoAccel((0,18),samples_per_read=1, 
                  host="192.168.152.1",
                  data_port=50044) 
    
    trig_imu.start()
    
    plt.ion()
    figure, (ax,ax2) = plt.subplots(2,1,figsize=(10*3,8*3))
    line1, = ax.plot(t, x_acc, label='x')
    line2, = ax.plot(t, y_acc, label='y')
    line3, = ax.plot(t, z_acc, label='z')
    ax.set_ylim(-2, 2)
    ax.set_title("Accelerometer")
    ax.set_xlabel("sample in buffer")
    ax.set_ylabel("acceleration/9.8 [ms^2]")
    # ax.legend(['x acceleration'],['y acceleration'],['z acceleration'])
    leg = ax.legend(loc="upper right")
    line4, = ax2.plot(t, x_gyro, label='x')
    line5, = ax2.plot(t, y_gyro, label='y')
    line6, = ax2.plot(t, z_gyro, label='z')
    # plt.title("Acceleration in X", fontsize=20)
    # plt.xlabel("sample")
    # plt.ylabel("acceleration")
    ax2.set_ylim(-200, 200)
    ax2.set_title("Gyroscope")
    ax2.set_xlabel("sample in buffer")
    ax2.set_ylabel("angular velocity [deg/s]")


    for i in range(100):
        new_data=trig_imu.read() 
        
        if len(x_acc) >= 20:
            x_acc = np.delete(x_acc,0)
            y_acc = np.delete(y_acc,0)
            z_acc = np.delete(z_acc,0)  
            x_gyro = np.delete(x_gyro,0)
            y_gyro = np.delete(y_gyro,0)
            z_gyro = np.delete(z_gyro,0)
            

        x_acc = np.append(x_acc,new_data[0].mean())
        y_acc = np.append(y_acc,new_data[1].mean())
        z_acc = np.append(z_acc,new_data[2].mean())
        x_gyro = np.append(x_gyro,new_data[3].mean())
        y_gyro = np.append(y_gyro,new_data[4].mean())
        z_gyro = np.append(z_gyro,new_data[5].mean())
        
        # line1.set_xdata(t)
        line1.set_ydata(x_acc)
        line2.set_ydata(y_acc)
        line3.set_ydata(z_acc)
        line4.set_ydata(x_gyro)
        line5.set_ydata(y_gyro)
        line6.set_ydata(z_gyro)

        figure.canvas.draw()
        figure.canvas.flush_events()
        #time.sleep(0.1)

    trig_imu.stop()
    
    plt.show(block=True)

def plotEMGdata():
    buffer_size = 2000
    emg = np.zeros(buffer_size)
    t = np.linspace(1,buffer_size,buffer_size)
    trig_emg=TrignoEMG((0,1),samples_per_read=1, 
                host="192.168.152.1",
                units="mV",
                data_port=50043) 
    # trig_emg.set_channel_range((0, 4))
    trig_emg.start()

    plt.ion()
    figure, (ax) = plt.subplots(1,1,figsize=(10*3,8*3))
    line1, = ax.plot(t, emg, label='x')
    ax.set_ylim(-4, 4)
    ax.set_title("EMG")
    ax.set_xlabel("sample in buffer")
    ax.set_ylabel("muscle activity [mV]")

    for i in range(1000):
        emg_data=trig_emg.read()

        if len(emg) >= buffer_size:
            for _ in range(len(emg_data[0])):
                emg = np.delete(emg,0) 

        for i in range(len(emg_data[0])):
            emg = np.append(emg,emg_data[0][i])

        line1.set_ydata(emg)

        figure.canvas.draw()
        figure.canvas.flush_events()

    trig_emg.stop()

#plotIMUdata()
plotEMGdata()