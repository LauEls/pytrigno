import argparse
from pytrigno import TrignoCommand, TrignoData

if __name__=="__main__":
    # Read the host ip from the command line if available
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost", type=str)
    args = parser.parse_args()
    host_ip = args.host
    #host_ip = "192.168.152.1"

    # Initialize the Command and the Data Ports
    trig_cmd = TrignoCommand(host=host_ip)
    trig_data = TrignoData(sensor_range=(0,3),host=host_ip)
 
    # Send a start broadcasting command to the host machine
    trig_cmd.start()

    for i in range(10):
        # Read new EMG and IMU data
        new_emg_data = trig_data.readEMG()
        new_aux_data = trig_data.readIMU()

        print("EMG Data:")
        print(new_emg_data)
        print("Accelerometer and Gyroscope Data:")
        print(new_aux_data)

    # Send a stop broadcasting command to the host machine
    trig_cmd.stop()
    