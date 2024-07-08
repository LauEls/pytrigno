import socket
import struct
import numpy


class TrignoCommand(object):
    """
    Command Port for Delsys Trigno wireless EMG system.

    Requires the Trigno Control Utility to be running.

    Parameters
    ----------
    host : str
        IP address the TCU server is running on.
    cmd_port : int
        Port of TCU command messages.
    timeout : float
        Number of seconds before socket returns a timeout exception.

    Attributes
    ----------
    CMD_TERM : str
        Command string termination.

    Notes
    -----
    Implementation details can be found in the Delsys SDK reference:
    https://delsys.com/downloads/USERSGUIDE/trigno/sdk.pdf
    """  
    CMD_TERM = '\r\n\r\n'

    def __init__(self, host='localhost', cmd_port=50040, timeout=10):
        self.host = host
        self.cmd_port = cmd_port
        self.timeout = timeout

        self._comm_socket = socket.create_connection(
            (self.host, self.cmd_port), self.timeout)
        self._comm_socket.recv(1024)

    def start(self):
        """
        Tell the device to begin streaming data.

        You should call ``read()`` soon after this, though the device typically
        takes about two seconds to send back the first batch of data.
        """
        resp = self._send_cmd('START')
        s = str(resp)
        if 'OK' not in s:
            print("warning: TrignoDaq command failed: {}".format(s))
    
    def stop(self):
        """Tell the device to stop streaming data."""
        resp = self._send_cmd('STOP')
        s = str(resp)
        if 'OK' not in s:
            print("warning: TrignoDaq command failed: {}".format(s))

    def _send_cmd(self, command):
        self._comm_socket.send(self._cmd(command))
        resp = self._comm_socket.recv(128)
        return resp

    @staticmethod
    def _cmd(command):
        return bytes("{}{}".format(command, TrignoCommand.CMD_TERM),
                     encoding='ascii')
    
class TrignoData(object):
    """
    Data Port for Delsys Trigno wireless EMG system to read EMG and IMU data.

    Requires the Trigno Control Utility to be running.

    Parameters
    ----------
    sensor_range : tuple with 2 ints
        Range of Sensor IDs to read from. Each sensor has a single EMG
        and nine IMU channels.
    host : str, optional
        IP address the TCU server is running on. By default, the device is
        assumed to be attached to the local machine.
    cmd_port : int, optional
        Port of TCU command messages.
    emg_port : int, optional
        Port of TCU EMG data access. By default, 50043 is used, but it is
        configurable through the TCU graphical user interface.
    imu_port : int, otional
        Port of TCU AUX data access. Recieves all auxiliary non-EMG data, 
        specifically accelerometer and gyroscope data. By default, 50044 is used, but it is
        configurable through the TCU graphical user interface.
    timeout : float, optional
        Number of seconds before socket returns a timeout exception.

    Attributes
    ----------
    BYTES_PER_CHANNEL : int
        Number of bytes per sample per channel. EMG and accelerometer data
    """
    BYTES_PER_CHANNEL = 4

    def __init__(self, sensor_range=(0,3), host='localhost', emg_port=50043, imu_port=50044, timeout=10):
        self.host = host
        self.sensor_range = sensor_range
        self.emg_port = emg_port
        self.imu_port = imu_port
        self.timeout = timeout

        self.emg_data_channels = 16
        self.imu_data_channels = 144

        

        self._emg_socket = socket.create_connection(
            (self.host, self.emg_port), self.timeout)
        self._imu_socket = socket.create_connection(
            (self.host, self.imu_port), self.timeout)
        
    def readEMG(self):
        """
        Request EMG data from the device.

        Returns
        -------
        data : ndarray, shape=(num_sensors, num_samples)
            Data read from the device. Each channel is a row and each column
            is a point in time.
        """
        data = self.read(self._emg_socket, self.emg_data_channels)
        data = data[self.sensor_range[0]:self.sensor_range[1]+1, :]
        return data

    def readIMU(self):
        """
        Request IMU data from the device.
        
        Returns
        -------
        data : ndarray, shape=(num_sensors*9, num_samples)
            Data read from the device. Each channel is a row and each column
            is a point in time.
        """
        data = self.read(self._imu_socket, self.imu_data_channels)
        data = data[self.sensor_range[0]*9:self.sensor_range[1]*9+1, :]
        return data

    def read(self, data_socket: socket, data_channels: int):
        """
        Request data from the device. Retrieves all data transmitted up to 
        a maximum of 1 million bytes. The data is tranlated into float values
        and structured into an array.

        Parameters
        ----------
        data_socket : socket
            Read either from emg or imu port.
        data_channels : int
            Number of data channels per sample

        Returns
        -------
        data : ndarray, shape=(data_channels, num_samples)
            Data read from the device. Each channel is a row and each column
            is a point in time.
        """
        packet = bytes()
        try:
            packet = data_socket.recv(1000000)
        except socket.timeout:
            raise IOError("Device disconnected.")

        num_samples_recv = int(len(packet)/self.BYTES_PER_CHANNEL)
        data = numpy.asarray(
            struct.unpack('<'+'f'*num_samples_recv, packet))
        
        if len(data)%data_channels != 0:
            data = numpy.append(data,numpy.zeros(data_channels-len(data)%data_channels))
        
        data = numpy.transpose(data.reshape((-1, data_channels)))

        return data
    
