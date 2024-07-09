import numpy as np
from scipy import signal

def median_filter(data, f_size):
	lgth, num_signal=data.shape
	f_data=np.zeros([lgth, num_signal])
	for i in range(num_signal):
		f_data[:,i]=signal.medfilt(data[:,i], f_size)
	return f_data

def freq_filter(data, f_size, cutoff):
	# lgth, num_signal=data.shape
	# f_data=np.zeros([lgth, num_signal])
	# lpf=signal.firwin(f_size, cutoff, window='hamming')
	# for i in range(num_signal):
	# 	f_data[:,i]=signal.convolve(data[:,i], lpf, mode='same')
		
    num_signal=data.shape[0]
    # print("shape ", num_signal)
    f_data=np.zeros(num_signal)
    lpf=signal.firwin(f_size, cutoff, window='hamming')
    f_data=signal.convolve(data, lpf, mode='same')
    return f_data

def linear_envelope(data, f_sample, f_cutoff):
	#Full-wave rectification
	data_rect = abs(data)

	#Moving Average Window size
	w_size = f_sample/(2*f_cutoff)

	#Low-pass filter using moving average
	data_filtered = np.convolve(data_rect, np.ones(w_size)/w_size, mode='same')

	return data_filtered

