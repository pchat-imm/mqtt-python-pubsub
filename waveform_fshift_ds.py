## import requirement
import numpy as np
import scipy
import csv
# import matplotlib.pyplot as plt
# !python3 -m pip install py3gpp
# from py3gpp import *
# import sys
import os

import paho.mqtt.client as mqtt




# Set up client and callbacks
client = mqtt.Client()
# global count_work 
count_work = 0


# Define callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # client.publish("test/topic", payload="Hello MQTT", qos=0, retain=False)

# This is called when a message is received on a subscribed topic
def on_message(client, userdata, msg):
    print(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")
    if(msg.topic =="waveform_fshift_ds/start"):
      sampleRate = 15.36e6
      if os.environ['fshift'] == "end":
         print(".")
      
      else:
        fshift = float(os.environ['fshift'])
        print("load file")
        waveform = load_rx_srsRAN('./waveform_IQComplex_fllay.csv')
        print("freq_shift")
        rxWaveformFreqCorrected = waveform_fshift(fshift, sampleRate, waveform)
        rxWaveformDS = waveformDS(sampleRate, rxWaveformFreqCorrected)
        ## add function correlation
        print("run")

        client.publish("waveform_fshift_ds/work"+os.environ['fshift'], payload=fshift, qos=0, retain=False)

    else:
       global count_work
       count_work = count_work + 1
       count_complete(count_work)
       # return count_work
    
def count_complete(count_work):
    if(count_work == 3):
      # compare correlate
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
  # client.subscribe("waveform_fshift_ds/work0")
  # client.subscribe("waveform_fshift_ds/work1")
  # client.subscribe("waveform_fshift_ds/work2")
  # client.subscribe("waveform_fshift_ds/work3")
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