import time
import shutil
import os
import yaml
import tarfile
from io import BytesIO
from io import TextIOWrapper
from tngsdk.benchmark.generator import ServiceConfigurationGenerator
from tngsdk.benchmark.helper import ensure_dir, read_yaml, write_yaml
from tngsdk.benchmark.helper import parse_ec_parameter_key
import tngsdk.package as tngpkg
from tngsdk.benchmark.logger import TangoLogger
nsd_pkg_path=r"G:\Nsd_tar\example_ns.tar.gz"
original_nsd_archive = tarfile.open(nsd_pkg_path, 'r:gz')
output_nsd_stream = None
file_path=r"G:\Nsd_output\output_1_nsd.tar.gz"
print("inside test_nsd")
service_ex=r"G:\Nsd_tar\ped_example_vnf.yml"
output_nsd_stream = tarfile.open(file_path, "w:gz")
experiment_configurations=list()  
def _add_probes_in_nsd(nsd_contents, service_ex):
            print("inside add probes")
            constituent_vnfd = nsd_contents['nsd:nsd-catalog']['nsd'][0]['constituent-vnfd']
            max_idx=constituent_vnfd[0].get('member-vnf-index')
            for cv in constituent_vnfd:
                print("inside for in constituent_vnfd")
                if cv.get('member-vnf-index') > max_idx:
                   max_idx = cv.get('member-vnf-index')
                   print("max_ids", max_idx)
                   for mp in [{'name':'mp.input'},{'name':'mp.output'}]:
                   #for mp in service_ex[0].experiment.measurement_points:
                       mp_name=mp.get(name)
                       print("mp_name",name)           	        
                       #get mp.vm-name -> image #we dont need this as of now
                       # Step 1: Adding constituent vnfds for probes
                       constituent_vnfd.append({"member-vnf-index": max_idx+1,"vnfd-id-ref": mp_name})    
                       #Step 2:Adding probe vnfd connection point reference to vlds
                       vld = nsd_contents['nsd:nsd-catalog']['nsd'][0]['vld']
                       for vld_n in vld:
                           if vld_n.get('vim-network-name')=='mgmt':
                       # Management Network
                              vnfd_connection_point_ref=vld_n.get('vnfd-connection-point-ref')
                              vnfd_connection_point_ref.append({
                              'member-vnf-index-ref': max_idx+1,
                              'vnfd-connection-point-ref': 'eth1-mgmt',
                              'vnfd-id-ref': mp_name})
                       # Data Network
                           else:
                               vnfd_connection_point_ref=vld_n.get('vnfd_connection_point_ref')
                               vnfd_connection_point_ref.append({
                               'member-vnf-index-ref': max_idx+1,
                               'vnfd-connection-point-ref': 'eth0-data',
                               'vnf-id-ref': mp_name})
                       max_idx=max_idx+1
                       print(nsd_contents)

def _update_output_nsd_pkg(original_nsd_archive, output_nsd_stream, service_ex):
    print("inside update")
    for pkg_file in original_nsd_archive.getmembers():        
        member_name = pkg_file.name
        print("member_name", member_name)
        if member_name.endswith(".yaml") or member_name.endswith(".yml"):
           member_contents = original_nsd_archive.extractfile(pkg_file)
           nsd_contents = yaml.safe_load(member_contents)
           _add_probes_in_nsd(nsd_contents, service_ex[0])   
           new_nsd_ti = tarfile.TarInfo(member_name)
           print(new_nsd_ti)
           new_nsd_stream = yaml.dump(nsd_contents).encode('utf8')
           new_nsd_ti.size = len(new_nsd_stream)
           print( new_nsd_ti.size)
           buffer = BytesIO(new_nsd_stream)
           output_nsd_stream.addfile(tarinfo=new_nsd_ti, fileobj=buffer)
        else:
            output_nsd_stream.addfile(pkg_file, original_nsd_archive.extractfile(pkg_file))
            
_update_output_nsd_pkg(original_nsd_archive, output_nsd_stream, service_ex)


            

        