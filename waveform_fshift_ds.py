import numpy as np
import scipy
import csv
import os
import paho.mqtt.client as mqtt
from py3gpp import *

# Set up client and callbacks
client = mqtt.Client()

# init global parameter
count_fshift = 0    # to count number of received fshift

# Define callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # client.publish("test/topic", payload="Hello MQTT", qos=0, retain=False)

# This is called when a message is received on a subscribed topic
def on_message(client, userdata, msg):
    print(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")

    if(msg.topic =="waveform_fshift_ds/start"):
      # if fshift_end : do_nothing
      if os.environ['fshift'] == "end":
        pass
      
      # other fshift start to calculate frequency_shift and downsampling
      else:
        sampleRate = 15.36e6
        fshift = float(os.environ['fshift'])      ## receive input when running the script
        
        print("load")
        base_path_PSS = "./PSS_Seq"
        input_file = "./waveform_IQComplex_fllay.csv"
        waveform = load_rx_srsRAN(input_file)
        refWaveforms = load_PSS_seq(base_path_PSS)
        
        print("calculate")
        rxWaveformFreqCorrected = waveform_fshift(fshift, sampleRate, waveform)
        rxWaveformDS = waveformDS(sampleRate, rxWaveformFreqCorrected)
        temp_corr_ind, temp_corr_val = correlate(carrier, fshift, sampleRate, rxWaveformDS, refWaveforms)
        fshift_NID2, fshift_corr_ind, fshift_corr_val = peak_one_fshift(temp_corr_ind, temp_corr_val)

        # mqtt explorer show waveform_fshift_ds/fshift_0: 2 212843 0.5678
        payload_fshift_corr = f"{fshift_NID2},{fshift_corr_ind},{fshift_corr_val}"
        client.publish("waveform_fshift_ds/fshift_"+os.environ['fshift'], payload = payload_fshift_corr)

    else:
      # add number of calculated correlate of fshift
      global count_fshift # call to edit global parameter
      print("in count_fshift loop")
      count_fshift = count_fshift + 1
      count_complete(count_fshift)

      if(msg.topic =="waveform_fshift_ds/fshift_#"):
         

    
def count_complete(count_fshift):
    if(count_fshift == 2):
      # count_fshift here is local parameter
      # once calculate enough fshift of corr(rxWaveformDS, refWaveforms) - determine max corr
      # return sel_NID2, sel_corr_ind, sel_corr_val
      print("sum")


def on_publish(client, userdata, mid):
    print(f"Message {mid} published")



client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Set username and password for authentication
client.username_pw_set("user_staff6", "gv76seyLDNtP6Zgz3!WYYc!fK")
# Connect to the broker (default is localhost, port 1883)
client.connect("mqtt.lailab.online", 10001, 60)

if(os.environ['fshift'] == "end"):
  # fshift_end have to subscribe all fshift, to calculate count_fshift
  client.subscribe("waveform_fshift_ds/#")
else:
  client.subscribe("waveform_fshift_ds/start")

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

  # Start the MQTT client loop
  client.loop_forever()