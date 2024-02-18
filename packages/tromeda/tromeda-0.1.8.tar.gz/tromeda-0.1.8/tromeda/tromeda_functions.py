# -*- coding: utf-8 -*-
"""

@author: ulysses
"""

import toml
import re
import json
import datetime
import requests



def get_device_info_basic(base_url:str,timestamp:str,site:str,dev_type:str,dev_name='all') -> list:
    ## try using dev-tracker api
    deviceinfo = {}
    meta_dict_ls = []
    try:
       # url = f'{config_dict["basic_url"]}?date={timestamp}&site={site}&dev_type={dev_type}&dev_name={dev_name}'
        url = f'{base_url}?date={timestamp}&site={site}&dev_type={dev_type}&dev_name={dev_name}'
        metadata = requests.get(url).json()
        for c in metadata:
#            dev = metadata[f'{c}']['DEVICE']
#            camp = metadata[f'{c}']['HISTORY']['0']['pylarda_camp']
            meta_dict = metadata[f'{c}']
            meta_dict['timestamp'] = timestamp
            meta_dict_ls.append(meta_dict)
        return meta_dict_ls #deviceinfo 
    except Exception as e:
        print(f'Error: {e}')

def get_device_info(config_dict:dict,timestamp:str,site:str,dev_type:str,dev_name='all') -> list:
    ## try using dev-tracker api
    deviceinfo = {}
    meta_dict_ls = []
    try:
        url = f'{config_dict["basic_url"]}?date={timestamp}&site={site}&dev_type={dev_type}&dev_name={dev_name}'
        metadata = requests.get(url).json()
        for c in metadata:
#            dev = metadata[f'{c}']['DEVICE']
#            camp = metadata[f'{c}']['HISTORY']['0']['pylarda_camp']
            meta_dict = metadata[f'{c}']
            meta_dict['timestamp'] = timestamp
            meta_dict_ls.append(meta_dict)
        return meta_dict_ls #deviceinfo 
    except Exception as e:
        print(f'Error: {e}')

def get_data_base_dir_from_pylarda(config_dict:dict,meta_dict_ls:list,filetype_ls:list) -> dict:
    pylarda_basedir = config_dict['pylarda_basedir']
    all_campaigns_file = f'{pylarda_basedir}/larda-cfg/{config_dict["all_campaigns_file"]}'
    tomlcamp = toml.load(all_campaigns_file)

    data = {}
    for entry in meta_dict_ls:

        dev  = entry['device']
        dev_type  =entry['type']
        pid  = entry['pid']
        camp = entry['history']['0']['pylarda_camp']
        timestamp = entry['timestamp']
        if len(camp) > 0:
            pass
        else:
            continue

        data[dev] = {}
        if dev in config_dict["device_dict"]:
            dev_translator = config_dict["device_dict"][dev]
        else:
            dev_translator = dev
        param_file = tomlcamp[camp]['param_config_file']
        param_file = f'{pylarda_basedir}/larda-cfg/{param_file}'
        tomldat = toml.load(param_file)
        correct_system = ''
        ft_ls = []
        for system in tomldat.keys():
            for file_type in tomldat[system]['path'].keys():
                base_dir = tomldat[system]['path'][file_type]['base_dir']
                if re.search(dev_translator, base_dir, re.IGNORECASE):
                    correct_system = system
                    break
            if len(correct_system) > 0:
                break
        #print(correct_system)
        ft_ls = [i for i in tomldat[correct_system]['path'].keys()]
        connector_file = f'{pylarda_basedir}/larda-connectordump/{camp}/connector_{correct_system}.json'
        try:
            connector_file_json = open(connector_file)
            connector_dict = json.load(connector_file_json)
        except Exception:
            connector_dict = ""
            pass

#        data[dev][correct_system] = {}
        data[dev]['filetype'] = {}
        data[dev]['system'] = correct_system
        if len(filetype_ls) == 0:
            filetype_ls = ft_ls
        for ft in filetype_ls:
#           data[dev][correct_system][ft] = []
           data[dev]['filetype'][ft] = []

           if ft in connector_dict:
               filenames_ls = []
               for entry in connector_dict[ft]:
                   entry_date = re.split(r'-',str(entry[0][0]))[0]

                   if timestamp == entry_date:
                       filename = entry[1]
                       filename = re.split(r'^\.\/',filename)[1]
                       base_dir = tomldat[correct_system]['path'][ft]['base_dir']
                       full_filename = f"{base_dir}{filename}"
                       data[dev]['filetype'][ft].append(full_filename)

    return data

