## current task
1. use 1 sdr to transmit and see result of its csv, if it can plot with matlab
2. use 1 sdr to trasnmit and 1 sdr to receive in real-time
3. use this code


## to operate system
- open vscode with Ubuntu WSL (select symbol >< at bottom left)
- open terminal
- mnt folder
```
cd /mnt/d/workarea/together_python                                                                                                                                                                            
```
- install requirement
```
pip install -r requirement.txt
```

- run code using `env` to add fshift_input
(open terminal with how many works expected) \
```
fshift=0 env python3 waveform_fshift_ds.py 
fshift=30000 env python3 waveform_fshift_ds.py 
fshift=45000 env python3 waveform_fshift_ds.py 
fshift=end env python3 waveform_fshift_ds.py 
```
the `end` declare the end of works, its work is to summarize 

- open `mqtt explorer` to run the topic `waveform_fshift_ds/start`
all works (except work_end) will do calculation

### note: `pm2` is not worked because of limited rersource of the notebook in windows os

# current result
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
- have one node to listen all and determine max_fshift_corr
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