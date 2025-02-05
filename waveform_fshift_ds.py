import numpy as np
import scipy
import csv
import os
import paho.mqtt.client as mqtt

# Set up client and callbacks
client = mqtt.Client()
# global parameter to count number of work
count_work = 0

# Define callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # client.publish("test/topic", payload="Hello MQTT", qos=0, retain=False)

# This is called when a message is received on a subscribed topic
def on_message(client, userdata, msg):
    print(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")

    if(msg.topic =="waveform_fshift_ds/start"):
      # if work_end : do_nothing
      if os.environ['fshift'] == "end":
        pass
      
      # other work start to calculate frequency_shift and downsampling
      else:
        sampleRate = 15.36e6
        fshift = float(os.environ['fshift'])      ## receive input from when running the script
        
        print("load")
        waveform = load_rx_srsRAN('./waveform_IQComplex_fllay.csv')
        
        print("calculate")
        rxWaveformFreqCorrected = waveform_fshift(fshift, sampleRate, waveform)
        rxWaveformDS = waveformDS(sampleRate, rxWaveformFreqCorrected)

        ## add function correlation
        refWaveforms = load_PSS_seq()
        print("run")

        client.publish("waveform_fshift_ds/work"+os.environ['fshift'], payload=fshift, qos=0, retain=False)

    else:
       global count_work    # call to edit global parameter
       count_work = count_work + 1
       count_complete(count_work)

    
def count_complete(count_work):
    if(count_work == 3):
      # count_work here is local parameter
      ## start compare correlate
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
  # work_end have to subscribe all work, to calculate count_work
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


def load_PSS_seq():
  # base path
  base_path = '/home/chatchamon/workarea/npn_5g/bladeRF_txrx/based_IQ_find_NID2/trial/PSS_seq'
  NID2_val = [0,1,2]

  # Dictionary to store file path and refWaveform
  PSS_files = {}
  refWaveforms = {}

  # Generate file path and initialize refWaveform arrays
  # add lists in the dictionary
  for NID2 in NID2_val:
      PSS_files[f'NID2_{NID2}'] = f'{base_path}/NID2_{NID2}.csv'
      refWaveforms[f'NID2_{NID2}'] = []

  for NID2 in NID2_val:
      with open(PSS_files[f'NID2_{NID2}'], 'r') as f:
          reader = csv.reader(f)
          for row in reader:
              IQ_PSS = row[0].strip()     # get string
              IQ_PSS = complex(IQ_PSS)    # turn to complex
              refWaveforms[f'NID2_{NID2}'].append(IQ_PSS)
  return refWaveforms




if __name__ == "__main__":
  # sampleRate = 15.36e6
  # fshift = float(os.environ['fshift'])

  # print("load file")
  # waveform = load_rx_srsRAN('./waveform_IQComplex_fllay.csv')
  # print("freq_shift")
  # rxWaveformFreqCorrected = waveform_fshift(fshift, sampleRate, waveform)
  # rxWaveformDS = waveformDS(sampleRate, rxWaveformFreqCorrected)

  # print("run")

  # Start the MQTT client loop
  client.loop_forever()