import numpy as np
import scipy
import csv
import os
import matplotlib.pyplot as plt
from py3gpp import *
import scipy.signal

count_work = 0

def load_rx_srsRAN(input_file):
  waveform = []
  with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
      IQComplex = row[0].strip()
      IQComplex = IQComplex.replace('i','j')
      IQComplex = complex(IQComplex)
      waveform.append(IQComplex)
  return waveform

def waveform_fshift(fshift, sampleRate, waveform):
  t = np.arange(len(waveform))/sampleRate
  rxWaveformFreqCorrected = waveform * np.exp(-1j*2*np.pi*fshift*t)
  return rxWaveformFreqCorrected

def waveformDS(sampleRate, scs, syncSR, waveform):
  mu = 1
  scs = 15 * 2**mu
  syncNfft = 256                  # minimum FFT Size to cover SS burst
  syncSR = syncNfft * scs * 1e3
  rxWaveformDS = scipy.signal.resample_poly(waveform, syncSR, sampleRate)
  return rxWaveformDS

def load_PSS_seq(base_path_PSS):
  NID2_val = [0,1,2]

  # Dictionary to store file path and refWaveform
  PSS_files = {}
  refWaveforms = {}

  # Generate file path and initialize refWaveform arrays
  # add lists in the dictionary
  for NID2 in NID2_val:
      PSS_files[f'NID2_{NID2}'] = f'{base_path_PSS}/NID2_{NID2}.csv'
      refWaveforms[f'NID2_{NID2}'] = []

  for NID2 in NID2_val:
      with open(PSS_files[f'NID2_{NID2}'], 'r') as f:
          reader = csv.reader(f)
          for row in reader:
              IQ_PSS = row[0].strip()     # get string
              IQ_PSS = complex(IQ_PSS)    # turn to complex
              refWaveforms[f'NID2_{NID2}'].append(IQ_PSS)
  return refWaveforms


def correlate(carrier, fshifts, sampleRate, rxWaveformDS, refWaveforms):
  kPSS = np.arange((119-63), (119+64))    # np.arange(56, 183) # check on 3GPP standard 
  peak_value = np.zeros(3)    # array
  peak_index = np.zeros(3, 'int')
  t = np.arange(len(rxWaveformDS))/sampleRate

  for NID2 in np.arange(3, dtype='int'):
    temp = scipy.signal.correlate(rxWaveformDS, refWaveforms[f'NID2_{NID2}'],'valid')
    peak_index[NID2] = np.argmax(np.abs(temp))
    peak_value[NID2] = np.abs(temp[peak_index[NID2]])   
    print(f"NID2 {NID2}:", peak_index[NID2], peak_value[NID2])    
  return peak_index, peak_value

def peak_one_fshift(corr_indices, corr_values):
   NID2_max = np.argmax(corr_values)
   max_corr_val = corr_values[NID2_max]
   max_corr_ind = corr_indices[NID2_max]
   return NID2_max, max_corr_val, max_corr_ind
   

if __name__ == "__main__":
  base_path_PSS = "./PSS_Seq"
  input_file = "./waveform_IQComplex_fllay.csv"
  # fshift = float(os.environ['fshift'])
  fshift = 45000

  # init parameter
  sampleRate = 15.36e6
  nrbSSB = 20
  mu = 1
  scs = 15 * 2**mu
  syncNfft = 256                  # minimum FFT Size to cover SS burst
  syncSR = syncNfft * scs * 1e3
  carrier = nrCarrierConfig(NSizeGrid = nrbSSB, SubcarrierSpacing = scs)

  waveform = load_rx_srsRAN(input_file)
  rxWaveformFreqCorrected = waveform_fshift(fshift, sampleRate, waveform)
  rxWaveformDS = waveformDS(sampleRate, scs, syncSR, rxWaveformFreqCorrected)

  refWaveforms = load_PSS_seq(base_path_PSS)
  peak_index, peak_value = correlate(carrier, fshift, sampleRate, rxWaveformDS, refWaveforms)
  NID2, max_corr_val, max_corr_ind = peak_one_fshift(peak_index, peak_value)
  print(NID2, max_corr_ind, max_corr_val)




