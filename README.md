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
fshift=1 env python3 waveform_fshift_ds.py 
fshift=2 env python3 waveform_fshift_ds.py 
fshift=end env python3 waveform_fshift_ds.py 
```
the `end` declare the end of works, its work is to summarize 

- open `mqtt explorer` to run the topic `waveform_fshift_ds/start`
all works (except work_end) will do calculation

### note: `pm2` is not worked because of limited rersource of the notebook in windows os