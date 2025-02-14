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
  #'''load all PSS_seq to use as refWaveform'''
  NID2_val = [0,1,2]

  # Dictionary to store file path and refWaveform
  PSS_files = {}
  refWaveforms = {}

  # Generate file path and initialize refWaveform arrays - add lists in the dictionary
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
  # '''currently get user_input through terminal, will need to change to subscribe mqtt topic and get message'''
  fshift_corr = {}
  print("---get_all_fshift_corr---Entries data of fshifts (Example: 45000 1 212347 2.345):")

  while len(fshift_corr) < set_count_fshift:
    user_input = input("Enter fshift data: ").strip()   # remove unnecessary space and \n     # user_input = 45000 1 212347 2.345    
    parts = user_input.split()    # parts = ['45000', '1', '212347', '2.345']

    fshift_val      = int(parts[0])     # 45000 
    fshift_NID2     = int(parts[1])     # 1 
    fshift_corr_ind = int(parts[2])     # 212347 
    fshift_corr_val = float(parts[3])   # 2.345 

    # store correlated values in dictionary
    fshift_corr[f'fshift_{fshift_val}'] = {
       "fshift_data": fshift_val,
       "fshift_NID2": fshift_NID2,
       "fshift_corr_ind": fshift_corr_ind,
       "fshift_corr_val": fshift_corr_val
    }    
  print("---get_all_fshift_corr---fshift_corr: ", fshift_corr)

  if len(fshift_corr) == set_count_fshift:
     max_fshift_corr(fshift_corr)

  return fshift_corr

def max_fshift_corr(fshift_corr):
  # ''' select fshift that provide the highest corr_val '''
  # use list comprehension to get list of corr_val
  list_corrVal = [x['fshift_corr_val'] for x in fshift_corr.values()]
  max_ind = np.argmax(list_corrVal)  # find index of list_corrVal with max corr\
  # return fshift of fshift_corr.keys at the max_ind
  sel_fshift = list(fshift_corr.keys())[max_ind]    # fshift_corr.keys() = ['fshift_30000', 'fshift_45000'], sel_fshift = 'fshift_45000'
  # return NID2, corr_ind, corr_val at that fshift
  sel_NID2     = fshift_corr[sel_fshift]['fshift_NID2']
  sel_corr_ind = fshift_corr[sel_fshift]['fshift_corr_ind']
  sel_corr_val = fshift_corr[sel_fshift]['fshift_corr_val']
  print(f"---max_fshift_corr---sel_fshift {sel_fshift}, sel_NID2 {sel_NID2}, sel_corr_ind {sel_corr_ind}, sel_corr_val {sel_corr_val}")
  return sel_fshift, sel_NID2, sel_corr_ind, sel_corr_val

if __name__ == "__main__":
  get_all_fshift_corr()
  # example input
  # 30000 2 238938 0.577
  # 45000 1 212347 2.345
  # 0     2 63528  0.567
  