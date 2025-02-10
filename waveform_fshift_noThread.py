import numpy as np
import scipy
import csv
import os
from py3gpp import *

count_fshift = 0    # global parameter to count number of fshift

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

def waveformDS(sampleRate, waveform):
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
  corr_ind = np.zeros(3, 'int')    # array
  corr_val = np.zeros(3)
  t = np.arange(len(rxWaveformDS))/sampleRate

  for NID2 in np.arange(3, dtype='int'):
    temp = scipy.signal.correlate(rxWaveformDS, refWaveforms[f'NID2_{NID2}'],'valid')
    corr_ind[NID2] = np.argmax(np.abs(temp))
    corr_val[NID2] = np.abs(temp[corr_ind[NID2]])  
  return corr_ind, corr_val

def peak_one_fshift(corr_ind, corr_val):
  # one rxWaveformDS of a fshift with 3 refWaveforms 
  # input is 3 NID2 with 3 corr_ind and 3 corr_val 
  print("corr_ind ", corr_ind)
  print("corr_val ", corr_val)
  fshift_NID2 = np.argmax(corr_val)
  fshift_corr_val = corr_val[fshift_NID2]
  fshift_corr_ind = corr_ind[fshift_NID2]
  print("fshift_corr: ", {fshift_NID2}, {fshift_corr_val}, {fshift_corr_ind})    
  return fshift_NID2, fshift_corr_ind, fshift_corr_val


if __name__ == "__main__":
  # init parameter
  sampleRate = 15.36e6
  nrbSSB = 20
  mu = 1
  scs = 15 * 2**mu
  syncNfft = 256                  # minimum FFT Size to cover SS burst
  syncSR = syncNfft * scs * 1e3
  carrier = nrCarrierConfig(NSizeGrid = nrbSSB, SubcarrierSpacing = scs)
  fshift = 0

  base_path_PSS = "./PSS_Seq"
  input_file = "./waveform_IQComplex_fllay.csv"
  waveform = load_rx_srsRAN(input_file)
  refWaveforms = load_PSS_seq(base_path_PSS)
  print("calculate")

  rxWaveformFreqCorrected = waveform_fshift(fshift, sampleRate, waveform)
  rxWaveformDS = waveformDS(sampleRate, rxWaveformFreqCorrected)
  temp_corr_ind, temp_corr_val = correlate(carrier, fshift, sampleRate, rxWaveformDS, refWaveforms)
  fshift_NID2, fshift_corr_ind, fshift_corr_val = peak_one_fshift(temp_corr_ind, temp_corr_val)
