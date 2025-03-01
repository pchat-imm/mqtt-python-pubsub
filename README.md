# mqtt-python-pubsub
**Purpose**: correlate received waveform with PSS sequence fast, using MQTT in file `waveform_fshift_ds.py`

**Procedure**: 
- correlate waveformDS with 3 refWaveforms, where `waveformDS = received signal w/ frequency shift and downsample`, `refWaveform = PSS seq where NID2 = [0,1,2]` 
- Each node with its fshift, subscribe to the same topic, publish their correlation results.
- Then end_node that subscribe to all can determine the maximum correlation, return `sel_fshift, sel_NID2, sel_corr_ind, sel_corr_val`

## To operate system
- open vscode with Ubuntu WSL (select symbol >< at bottom left)
- open terminal (number of terminal = number of fshift)
- mnt folder
```
cd /mnt/d/workarea/together_python                                                                                                                                                                            
```
- install requirement
```
pip install -r requirement.txt
```
- set number of desired fshift `set_count_fshift = 4` in `waveform_fshift_ds.py`
- open number of terminal = set_count_fshift. each terminal run code with `env` with different fshift_input. With the end_node to subscribe all topics and find maximum fshift.
```
fshift=0 env python3 waveform_fshift_ds.py
fshift=15000 env python3 waveform_fshift_ds.py 
fshift=30000 env python3 waveform_fshift_ds.py 
fshift=45000 env python3 waveform_fshift_ds.py 
fshift=end env python3 waveform_fshift_ds.py 
```
- open `mqtt explorer` to start the topic `waveform_fshift_ds/start`
all nodes (except end_node) will start correlation

### note: `pm2` is not worked because of limited rersource of the notebook in the windows os

# Result
- use mqtt (subscribe/publish topic)
- open terminal according to number of desired fshift, for example
```
fshift=-45000 env python3 waveform_fshift_ds.py 
fshift=-30000 env python3 waveform_fshift_ds.py 
fshift=-15000 env python3 waveform_fshift_ds.py 
fshift=0 env python3 waveform_fshift_ds.py 
fshift=15000 env python3 waveform_fshift_ds.py
fshift=30000 env python3 waveform_fshift_ds.py
fshift=45000 env python3 waveform_fshift_ds.py 
```
- start end_node
```
fshift=end env python3 waveform_fshift_ds.py
```
- with sufficient input fshift determine max_correlation 
```
fshift_-45000: {'fshift_data': -45000, 'fshift_NID2': 2, 'fshift_corr_ind': 135710, 'fshift_corr_val': 0.07004893448160758}
fshift_-15000: {'fshift_data': -15000, 'fshift_NID2': 1, 'fshift_corr_ind': 74203, 'fshift_corr_val': 0.05985093644569733}
fshift_15000: {'fshift_data': 15000, 'fshift_NID2': 0, 'fshift_corr_ind': 135308, 'fshift_corr_val': 0.06483307552265592}
fshift_45000: {'fshift_data': 45000, 'fshift_NID2': 1, 'fshift_corr_ind': 211873, 'fshift_corr_val': 0.23058730841798264}
fshift_0: {'fshift_data': 0, 'fshift_NID2': 2, 'fshift_corr_ind': 212552, 'fshift_corr_val': 0.06803419198859888}
fshift_-30000: {'fshift_data': -30000, 'fshift_NID2': 2, 'fshift_corr_ind': 227784, 'fshift_corr_val': 0.06777558441911724}
fshift_30000: {'fshift_data': 30000, 'fshift_NID2': 1, 'fshift_corr_ind': 211873, 'fshift_corr_val': 0.1651347757924192}
len(fshift_corr) 7
---max_fshift_corr---sel_fshift fshift_45000, sel_NID2 1, sel_corr_ind 211873, sel_corr_val 0.23058730841798264  
```
<img src=https://github.com/user-attachments/assets/10b7c001-6ce4-45d8-bf96-7d04c0d12171>


