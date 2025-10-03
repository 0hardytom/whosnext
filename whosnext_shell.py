from datetime import datetime
import time
from astropy.io import ascii
from astropy.table import Table
from astropy.time import Time
import os
import numpy as np
import re


def safe_to_jd(date_str):
    if str(date_str).strip().lower() == 'not found':
        return np.nan
    try:
        dt_obj = datetime.strptime(str(date_str), '%m/%d/%y %H:%M')
        time_obj = Time(dt_obj, scale='utc')
        return time_obj.jd
    except ValueError:
        return np.nan

def initialise():
    data = Table(ascii.read('out.csv'))
    date_column = data['time'].copy()
    jd_column = np.array([safe_to_jd(d) for d in date_column], dtype=float)
    data['time'] = jd_column
    data = data[~np.isnan(data['time'].data)]
    data.sort('time')
    return data

def get_rows(ts,next:bool):
    nt = (Time.now().jd+1/24)+6
    modif = 0 if next else -1
    idx = np.sum(ts['time']<nt) + modif
    return ts[idx]

def process_name(dur_id:str, pref_name:str):
    surname = re.search(r" (\S+)\s*$", dur_id).group(1).lower().capitalize()
    firstname = pref_name.rstrip().capitalize()
    return firstname+' '+surname

if __name__ == '__main__':
    table = initialise()
    while True:
        now = get_rows(table,False)
        nxt = get_rows(table, True)

        names = ['current', 'next']

        for i,n in enumerate([now,nxt]):
            print('#############################################')
            print(f'This is the information for the {names[i]} candidate')
            print(f'Name: {process_name(n['\ufeffdur_id'], n['pref_name'])}')
            print(f'Email: {n['cisid']}')
            print(f'Phone #: {n['phone']}')
            print(f'They are auditioning on {n['inst']}')
            if n['doub'] != 'No':
                print(f'They are doubling on {n['doub']}')

            print(f'Ensemble Preference: {n['pref']}')
            print(f'Section Leadership?: {n['sl']}')
            
            if len(n['accessib']) > 1:
                print(f'Notes: {n['accessib']}')
            else:
                print(f'There are no accessibility requirements for this audition')
            print(f'{n['resp']}')
            print('#############################################')


        time.sleep(60)
    




