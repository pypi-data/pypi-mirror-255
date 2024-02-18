#!/usr/bin/env/pyhton3

# module imports
import numpy as np
import pandas as pd
import requests, json
import logging
from dotenv import load_dotenv, dotenv_values
import os, sys
from dataclasses import dataclass
import random
from tqdm import tqdm as tq
# loggin setup

load_dotenv()
config = dotenv_values("data.env")
logging.basicConfig(level=logging.CRITICAL)



# environment setup. (Migrate to .env)
# api_version = 1
# api_server = "https://vixen.hopto.org"
# contact_email = "r.tandon@rsaqua.co.uk"

api_server = config['API_SERVER']
api_version = config['API_VERSION']
contact_email = config['CONTACT_EMAIL']

@dataclass
class SignatureData:

    frequency_ts_np : np.array
    frequency_ts_pd : pd.DataFrame
    meta_data : {}
    
@dataclass
class SimulationData:
    
    frequency_ts_np : np.array
    frequency_ts_pd : pd.DataFrame
    meta_data : {}
    snapshot : bool = True

class MarlinData(object):
    
    def __init__(self, load_args : {} = {}):
        """Initialise MarlinData object. Define all data structures required. 
        """        
    
        self.snapshot_ids = []              # list of signature snapshot ids
        self.sim_snapshot_ids = []          # list of sim snapshot ids
        self.run_ids = []                   # list of run ids
        self.signature_ids = []             # list of signature ids
        self.number_runs = 0                # number of runs in signature data
        self.number_signatures = 0          # number of signatures in data set
        self.number_snapshots = 0           # number of sig snapshots      
        self.number_sim_snapshots = 0       # number of sim snapshots

        self.signature_data = {}            # signature data. Dictionary of SignatureData.
        self.signature_index = []
        self.simulation_data = {}           # simulation data. Dictionary of SimulationData.
        self.simulation_index = []
        if 'limit' in load_args:
            self.limit_sig = load_args['limit']
        else:
            self.limit_sig = 5
            
        
        
    def download_signatures(self, load_args : {} = {}) -> ({}):
        """Load binary data from RSA server and load into corresponding numpy arrays and pandas datasets.

        Args:
            load_args (dict, optional): Load arguments. E.g. time and location contraints. Defaults to {}.

        Returns:
            {}: Dictionary 
        """   
        
        signature_enpoint = "data/signature"
        api_url = f"{api_server}/rs/api/v{api_version}/{signature_enpoint}"
        
        try:
            r = requests.get(api_url) 
            request_json_data_signature = r.json()['data']

        except:
            logging.critical(f"[marlin_data.py] Unable to run signature retrieval api request. Email {contact_email}")

        for signature in request_json_data_signature:
            
            # Filter---
            if 'signature_ids' in load_args:
                if signature['snapshot_id'] not in load_args['signature_ids']:
                    continue
           
            # ----
            
            # --
            # Build tag and id trackers for data object
            # --
            
            if signature['snapshot_id'] not in self.snapshot_ids:
                self.snapshot_ids.append(signature['snapshot_id'])
                
            if signature['run_id'] not in self.run_ids:
                self.run_ids.append(signature['run_id'])
                
            if signature['signature_id'] not in self.signature_ids:
                self.signature_ids.append(signature['signature_id'])
            
        
       
        # limit_sig = 5
        limit_sig_cnt = 0
        for snapshot_id in self.snapshot_ids:
            if limit_sig_cnt > self.limit_sig:
                break
            # -- 
            # We have the signature id now and require snapshot data in order to build metadata, e.g. delta t, time and location id.
            # We now grab all the meta data for the signature
            # --
            
            # print (f'Running for snapshot id {snapshot_id}')
            
            # get the snapshot id of the snapshot xr with signature
            # snapshot_id = signature['snapshot_id']
            snapshot_id = snapshot_id            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/data"
            snapshot_data_signature_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            
            # make api request
            try:
                
                r_ss = requests.get(snapshot_data_signature_url) 
                request_json_data_snapshot = r_ss.json()['data'][0]
                meta_data = self.parse_meta(snapshot_data = request_json_data_snapshot)
                
            except:
                logging.debug(f"[marlin_data.py - 2] Unable to run snapshot data retrieval api request. Email {contact_email}")
    
            # --
            # Get serial data : meta data complete, download and convert the stored serial data
            # --
            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/serialdata"
            snapshot_serial_data_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            # make api request
            try:
               
                r_serial = requests.get(snapshot_serial_data_url) 
                request_json_serial_data = r_serial.json()['data'][0]
                
                domain_data_np, domain_data_pd = self.deserial_data(raw_data = request_json_serial_data['json_raw'])
                sim_data = SignatureData(frequency_ts_np = domain_data_np, frequency_ts_pd = domain_data_pd, meta_data = meta_data)
                self.signature_data[snapshot_id] = sim_data
                self.signature_index.append(snapshot_id)
                
                # if domain_data_np or domain_data_pd == None:
                #     logging.debug(f"[marlin_data.py -3] {snapshot_id} Empty serial data file for snapshot raw data.Email {contact_email} ")
                    
                
            except:
                logging.debug(f"[marlin_data.py - 5] Unable to run snapshot data retrieval api request. Email {contact_email}")
    
            limit_sig_cnt += 1

        # set length parameters
        self.number_runs = len(self.run_ids)
        self.number_snapshots = len(self.snapshot_ids)
        self.number_signatures = len(self.signature_index)
        
        return self.signature_data, self.signature_index
             
    def download_simulation_snapshots(self, load_args = {}) -> ({}):
        """Load binary data from RSA server and load into corresponding numpy arrays and pandas datasets.

        Args:
            load_args (dict, optional): _description_. Defaults to {}.

        Returns:
            bool: _description_
        """   
        
        snapshot_endpoint = "data/snapshot/data/all"
        api_url = f"{api_server}/rs/api/v{api_version}/{snapshot_endpoint}"
        
        try:
            r = requests.get(api_url) 
            request_json_data_snapshots = r.json()['data']

        except:
            logging.critical(f"[marlin_data.py] Unable to run all snapshots retrieval api request. Email {contact_email}")
        
        
        
        limit_sig_cnt = 0
        for snapshot in request_json_data_snapshots:
            if limit_sig_cnt > self.limit_sig:
                break
            # --
            # Build tag and id trackers for data object
            # --
            # logging.debug(load_args['ss_ids'])
            
            # logging.debug(f'ss_id{snaphsot['ss_id']}')
            # Filter---
            if 'ss_ids' in load_args:
                if snapshot['ss_id'] not in load_args['ss_ids']:
                    
                    continue
            if 'location' in load_args:
                if snapshot['data_receiver_location_name'] not in load_args['location']:
                    continue
            # ----
            
            if snapshot['ss_id'] not in self.snapshot_ids:
                self.sim_snapshot_ids.append(snapshot['ss_id'])
                limit_sig_cnt += 1
            # if snapshot['run_id'] not in self.run_ids:
            #     self.sim_run_ids.append(signature['run_id'])
                
           
        
        for snapshot_id in self.sim_snapshot_ids:
           
            # -- 
            # We have the signature id now and require snapshot data in order to build metadata, e.g. delta t, time and location id.
            # We now grab all the meta data for the signature
            # --
            
            # print (f'Running for snapshot id {snapshot_id}')
            
            # get the snapshot id of the snapshot xr with signature
            # snapshot_id = signature['snapshot_id']
            snapshot_id = snapshot_id            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/data"
            snapshot_data_signature_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            
            
            # make api request
            try:
                r_ss = requests.get(snapshot_data_signature_url) 
                request_json_data_snapshot = r_ss.json()['data'][0]
                
                #filter location
                
                    
                
                meta_data = self.parse_meta(snapshot_data = request_json_data_snapshot)
               
            except:
                logging.critical(f"[marlin_data.py - 2] Unable to run snapshot data retrieval api request. Email {contact_email}")
    
            # --
            # Get serial data : meta data complete, download and convert the stored serial data
            # --
            
            #define API endpoint & url
            snapshot_data_signature_enpoint = "data/snapshot/serialdata"
            snapshot_serial_data_url = f"{api_server}/rs/api/v{api_version}/{snapshot_data_signature_enpoint}/{snapshot_id}"
            # print (snapshot_serial_data_url)
            # make api request
            try:
                
                r_serial = requests.get(snapshot_serial_data_url)
                try: 
                    request_json_serial_data = r_serial.json()['data'][0]
                    # print (request_json_serial_data)
                except:
                    # no data
                    continue
                
                if "success" in r_serial.json()['data'][0]:
                    continue
                    
                # print (request_json_serial_data['json_raw'])
                domain_data_np, domain_data_pd = self.deserial_data(raw_data = request_json_serial_data['json_raw'])
                sig_data = SimulationData(frequency_ts_np = domain_data_np, frequency_ts_pd = domain_data_pd, meta_data = meta_data)
                self.simulation_data[snapshot_id] = sig_data
                self.simulation_index.append(snapshot_id)
                # if domain_data_np or domain_data_pd == None:
                #     logging.debug(f"[marlin_data.py -3] {snapshot_id} Empty serial data file for snapshot raw data.Email {contact_email} ")
                    
                
            except:
                logging.critical(f"[marlin_data.py - 5] Unable to run snapshot data retrieval api request. Email {contact_email}")
    

        # set lenght parameters
        self.number_sim_snapshots = len(self.sim_snapshot_ids)
        
        return self.simulation_data, self.simulation_index
     
    def parse_meta(self, snapshot_data : {} = None) -> {}:
        
        meta_data = {}
        meta_data['snapshot_id '] = snapshot_data['ss_id']
        meta_data['data_frame_start'] = snapshot_data['data_frame_start']
        meta_data['data_frame_end'] = snapshot_data['data_frame_end']
        meta_data['listener_location'] = snapshot_data['data_receiver_location']
        meta_data['location_name'] = snapshot_data['data_receiver_location_name']
        meta_data['frame_delta_t'] = snapshot_data['data_delta_time']
        meta_data['sample_rate'] =  snapshot_data['sample_rate']
        return meta_data
    
    def deserial_data(self, raw_data : {} = None) -> (np.array, pd.DataFrame):
       
        # print (raw_data)
        np_data, pd_data, c = (None, None, None)
        # print (raw_data['raw_data_url'])
        random_tag = random.randint(0,99999)
        # pandas_data = None
        # c = None
        if 'raw_data_url' in raw_data:
            # print ("file")
            serial_domain_data_fn = raw_data['raw_data_url']
            # print (serial_domain_data_fn)
            r = requests.get(serial_domain_data_fn, allow_redirects=True, stream=True)
            
            total_length = r.headers.get('content-length')
            # print (f'Length: {total_length} {serial_domain_data_fn}')
            print (f"[Marlin Data : Fetching binary data : {serial_domain_data_fn}]")
            # print ("file")
            f = open(f'streamed_file{random_tag}', 'wb')
            dl = 0
            total_length = int(total_length)
            
            for data in r.iter_content(chunk_size=2000):
                dl += len(data)
                f.write(data)
                done = int(50* dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
                sys.stdout.flush()

            sys.stdout.flush()

            with open(f'streamed_file{random_tag}', 'rb') as fr:
                c = fr.read()
            
            dt = np.dtype("float32")
            np_data  = np.frombuffer(c, dtype=dt)
            pd_data = pd.DataFrame(np_data)
            fr.close()

            
        return np_data, pd_data
           
class MarlinDataStreamer(object):
   
    def __init__(self):
       
        self.data_feed = {}
        self.data_ids = []
        self.feed_index = -1
        self.data_vec_length = 0
    
    def init_data(self, data_feed : {} = {}, data_ids : [] = []) -> None:
        
        # initiaslise vector of feed epoch ids
        self.data_ids = data_ids
        
        # initialise the feed dataset
        self.data_feed = data_feed
        
        # determin lenght of data feed
        self.data_vec_length = len(self.data_ids)
        
        # start data feed
        self.feed_index = 0
        
    def __iter__(self):
        return self
        
    def __next__(self):
        if self.feed_index >= self.data_vec_length:
            self.feed_index = 0
            raise StopIteration
        
        feed_value = self.data_feed[self.data_ids[self.feed_index]]
        self.feed_index += 1
        return feed_value


if __name__ == "__main__":
    
    """--- Tutorial / Quick Start ---
    Download both signature data & run data for use in a ML / simulation setup.
    """
    
    # 1. instantiate a Marlin Data object
    marlin_data = MarlinData()
    # 2. download signatures from RSA signature database
    #marlin_data.download_signatures()
    # 3. download simulation / ML run snapshot data
    marlin_data.download_simulation_snapshots()
    
    # 4. create a datafeed from the downloaded snapshot data
    data_feed = MalrinDataStreamer()
    data_feed.init_data(marlin_data.simulation_data, marlin_data.simulation_index)
    
    # 5. access and print data feed
    for data_inst in data_feed:
        print (data_inst)
    
    #---