import tromeda.tromeda_functions as tromeda
import json

config_file = ''
with open(config_file,"r") as con_file:
            config_dict = json.load(con_file)

#meta_dict_ls = tromeda.get_device_info(config_dict=config_dict, timestamp='20231207', site='eriswil', dev_type='halo')
#print(meta_dict_ls)
meta_dict_ls = tromeda.get_device_info(config_dict=config_dict, timestamp='20231107', site='leipzig', dev_type='polly')
for entry in meta_dict_ls:
#    print(entry)
    print(entry['DEVICE'])
#    print(entry['HISTORY']['0']['CAMPAIGN'])
    print(entry['HISTORY']['0']['pylarda_camp'])

#data = tromeda.get_data_base_dir_from_pylarda(config_dict=config_dict,meta_dict_ls=meta_dict_ls,filetype_ls=['scans'])
#data = tromeda.get_data_base_dir_from_pylarda(config_dict=config_dict,meta_dict_ls=meta_dict_ls,filetype_ls=[])
#print(data)

