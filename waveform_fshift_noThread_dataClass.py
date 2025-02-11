import numpy as np
import scipy
import csv
import os
from py3gpp import *

# init global paramter
count_fshift = 0    # global parameter to count number of fshift
set_count_fshift = 2
fshift_corr = {}

def load_rx_srsRAN(input_file):
  #'''load a file of receive signal from base station (SDR) using srsRAN'''
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
  # '''frequency shift waveform'''
  t = np.arange(len(waveform))/sampleRate
  rxWaveformFreqCorrected = waveform * np.exp(-1j*2*np.pi*fshift*t)
  return rxWaveformFreqCorrected

def waveformDS(sampleRate, waveform):
  # '''downsampling waveform'''
  mu = 1
  scs = 15 * 2**mu
  syncNfft = 256                  # minimum FFT Size to cover SS burst
  syncSR = syncNfft * scs * 1e3
  rxWaveformDS = scipy.signal.resample_poly(waveform, syncSR, sampleRate)
  return rxWaveformDS

def load_PSS_seq(base_path_PSS):
  #'''load all PSS_seq'''
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
   # '''correlate 1 rxWaveformDS of a fshift with 3 refWaveforms''' 
  kPSS = np.arange((119-63), (119+64))    # np.arange(56, 183) # check on 3GPP standard 
  corr_ind = np.zeros(3, 'int')    # array
  corr_val = np.zeros(3)
  t = np.arange(len(rxWaveformDS))/sampleRate

  for NID2 in np.arange(3, dtype='int'):
    temp = scipy.signal.correlate(rxWaveformDS, refWaveforms[f'NID2_{NID2}'],'valid')
    corr_ind[NID2] = np.argmax(np.abs(temp))
    corr_val[NID2] = np.abs(temp[corr_ind[NID2]])
    print("corr_ind ", corr_ind)
    print("corr_val ", corr_val)  
  return corr_ind, corr_val

def peak_one_fshift(corr_ind, corr_val):
  # '''get peak corr_val of the fshift (rxWaveformDS with 3 refWaveforms)'''
  # input is 3 NID2 with 3 corr_ind and 3 corr_val 
  fshift_NID2 = np.argmax(corr_val)
  fshift_corr_val = corr_val[fshift_NID2]
  fshift_corr_ind = corr_ind[fshift_NID2]
  print("fshift_corr: ", {fshift_NID2}, {fshift_corr_val}, {fshift_corr_ind})    
  return fshift_NID2, fshift_corr_ind, fshift_corr_val

def get_all_fshift_corr():
  # '''currently get user_input through terminal, will need to change to subscribe topic and get message'''
  fshift_corr = {}
  print("Entries data of 3 fshifts:")
  print("Enter data in the format: fshift NID2 corr_ind corr_val")
  print("Example: 45000 1 212347 2.345")

  while len(fshift_corr) < set_count_fshift:
    # user_input = 45000 1 212347 2.345
    # parts = ['45000', '1', '212347', '2.345']
    user_input = input("Enter fshift data: ").strip()   # remove unnecessary space and \n 
    # print("user_input: ", user_input)

    parts = user_input.split()
    # print("parts: ", parts)

    fshift_data     = int(parts[0])     # 45000 (int)
    fshift_NID2     = int(parts[1])     # 1 (int)
    fshift_corr_ind = int(parts[2])     # 212347 (int)
    fshift_corr_val = float(parts[3])   # 2.345 (float)

    # print("fshift %d, fshift_NID2 %d, fshift_corr_ind %d, fshift_corr_val %f" %(fshift_data, fshift_NID2, fshift_corr_ind, fshift_corr_val))

    # store correlated values in dictionary
    fshift_corr[f'fshift_{fshift_data}'] = {
       "fshift_data": fshift_data,
       "fshift_NID2": fshift_NID2,
       "fshift_corr_ind": fshift_corr_ind,
       "fshift_corr_val": fshift_corr_val
    }
    
  print(fshift_corr)
  print("len(fshift_corr): ", len(fshift_corr))

  if len(fshift_corr) == set_count_fshift:
     sel_fshift(fshift_corr)

  return fshift_corr

def sel_fshift(fshift_corr):
  # ''' select fshift that provide the highest corr_val '''
  fshift_corr_vals = list(x["fshift_corr_val"] for x in fshift_corr.values())
  # print("fshift_corr_vals", fshift_corr_vals) 

  ind_max_corr = np.argmax(fshift_corr_vals)
  # print("ind_max_corr", ind_max_corr)

  # keys: fshift_30000, fshift_0, fshift_45000
  max_fshift_key = list(fshift_corr.keys())[ind_max_corr]
  print("max_fshift_key", max_fshift_key)

  print(fshift_corr[max_fshift_key])

  return fshift_corr[max_fshift_key]
   



if __name__ == "__main__":
  # init parameter
  # sampleRate = 15.36e6
  # nrbSSB = 20
  # mu = 1
  # scs = 15 * 2**mu
  # syncNfft = 256                  # minimum FFT Size to cover SS burst
  # syncSR = syncNfft * scs * 1e3
  # carrier = nrCarrierConfig(NSizeGrid = nrbSSB, SubcarrierSpacing = scs)
  # fshift = 0

  # base_path_PSS = "./PSS_Seq"
  # input_file = "./waveform_IQComplex_fllay.csv"
  # waveform = load_rx_srsRAN(input_file)
  # refWaveforms = load_PSS_seq(base_path_PSS)
  # print("calculate")

  # rxWaveformFreqCorrected = waveform_fshift(fshift, sampleRate, waveform)
  # rxWaveformDS = waveformDS(sampleRate, rxWaveformFreqCorrected)
  # temp_corr_ind, temp_corr_val = correlate(carrier, fshift, sampleRate, rxWaveformDS, refWaveforms)
  # fshift_NID2, fshift_corr_ind, fshift_corr_val = peak_one_fshift(temp_corr_ind, temp_corr_val)
  
  get_all_fshift_corr()