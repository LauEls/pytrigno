import numpy as np
import csv
import threading
import time

emg_data = np.zeros((1,4))
aux_data = np.zeros((1,24))

def getEMG():
    emg_data = np.random.rand(4,20)*10
    time.sleep(0.1)
    return emg_data

def getAUX():
    acc_data = np.random.rand(24,20)*100
    time.sleep(0.1)
    return acc_data


def readData(stop_event):
     global emg_data, aux_data
     while not stop_event.is_set():
        print("This is a repeated message.")
        new_emg_data = getEMG()
        emg_data = np.concatenate((emg_data,np.transpose(new_emg_data)),axis=0)
        new_aux_data = getAUX()
        aux_data = np.concatenate((aux_data,np.transpose(new_aux_data)),axis=0)

def writeCSV(file_path, title, data):
    with open(file_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(title)
        csvwriter.writerows(data)



if __name__=="__main__":
    dt = time.strftime("%Y%m%d-%H%M%S")
    print("Enter file name:")
    rec_name = input()
    emg_file = "data/"+rec_name+"_emg_"+str(dt)+".csv"
    aux_file = "data/"+rec_name+"_aux_"+str(dt)+".csv"
    print(emg_data)

    emg_first = ['EMG Sensor 1', 'EMG Sensor 2', 'EMG Sensor 3', 'EMG Sensor 4']
    aux_first = ['accelerometer x sensor 1', 'accelerometer y sensor 1', 'accelerometer z sensor 1',
                 'gyroscope x sensor 1', 'gyroscope y sensor 1', 'gyroscope z sensor 1',
                 'accelerometer x sensor 2', 'accelerometer y sensor 2', 'accelerometer z sensor 2',
                 'gyroscope x sensor 2', 'gyroscope y sensor 2', 'gyroscope z sensor 2',
                 'accelerometer x sensor 3', 'accelerometer y sensor 3', 'accelerometer z sensor 3',
                 'gyroscope x sensor 3', 'gyroscope y sensor 3', 'gyroscope z sensor 3',
                 'accelerometer x sensor 4', 'accelerometer y sensor 4', 'accelerometer z sensor 4',
                 'gyroscope x sensor 4', 'gyroscope y sensor 4', 'gyroscope z sensor 4',]

    stop_event = threading.Event()

    print("Press Enter to start...")
    input()
    
    read_data_thread = threading.Thread(target=readData, args=(stop_event,))
    read_data_thread.start()

    print("Press Enter again to stop...")
    input()

    stop_event.set()
    read_data_thread.join()

    print("Printing stopped.")
    print(emg_data.shape)
    print(aux_data.shape)
    writeCSV(emg_file, emg_first, emg_data)
    writeCSV(aux_file, aux_first, aux_data)
    