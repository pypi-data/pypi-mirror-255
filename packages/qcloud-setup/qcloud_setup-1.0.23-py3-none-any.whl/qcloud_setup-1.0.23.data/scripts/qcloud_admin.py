#!python

import yaml
import boto3
import demjson3
import paramiko
import botocore

import os
import re
import sys
import tty
import json
import select
import socket
import termios
import logging
import pathlib
import argparse
import requests
import traceback
import subprocess
import configparser

from pick import pick
from time import sleep, time
from pathlib import Path
from pprint import pprint
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict

import importlib.resources 


SOURCE_SNAPSHOT = "snap-0d33b6992599a1967"
SOURCE_REGION   = "us-east-1"
VERSION         = "v6.1.0"
DEBUG           = False


def debug(s):
    if DEBUG: pprint(s)
 

class tcol:
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN    = '\033[96m'
    ENDC    = '\033[0m'



class QCloudError(Exception):
    pass



def progress(count):
    chars = [ '[>     ]', '[=>    ]', '[ =>   ]', '[  =>  ]',
              '[   => ]', '[    =>]', '[     =]', '[      ]',
              '[     <]', '[    <=]', '[   <= ]', '[  <=  ]',
              '[ <=   ]', '[<=    ]', '[=     ]', '[      ]']
    return chars[count % len(chars)]



def checklist(key, value="", check=False):
    verbose = True
    tick = u'\u2713'
    if verbose and check:
       print(f"{tcol.GREEN}[{tick}]{tcol.ENDC} {key: <42} {value}")
    elif verbose:
       print(f"{tcol.GREEN}[ ]{tcol.ENDC} {key: <42} {value}", end='\r')


def checklist_failed(key, value=""):
    print(f"{tcol.RED}[x]{tcol.ENDC} {key: <42} {value}")




def checklist_with_progress(key, status, count):
    prog = progress(count)
    if status:
       print(f"{tcol.GREEN}[ ]{tcol.ENDC} {key: <42} {status} {tcol.BLUE}{prog}{tcol.ENDC}", end='\r')
    else:
       print(f"{tcol.GREEN}[ ]{tcol.ENDC} {key: <42} {tcol.BLUE}{prog}{tcol.ENDC}", end='\r')



def watch_snapshot_progress(session, snapshot_id):
    client = session.client('ec2')
    done   = False
    
    while not done:
        response = client.describe_snapshots(SnapshotIds=[snapshot_id])
        snapshot = response['Snapshots'][0]
        prog = snapshot['Progress']

        if prog == "100%":
            checklist("Migrating Q-Cloud software","COMPLETE ", True)
            return
        else:
            for i in range(128):
                checklist_with_progress("Migrating Q-Cloud software", "", i)
                #checklist("Migrating Q-Cloud software","{}".format(progress(i)))
                sleep(0.1)



def remove_snapshot(session, snapshot_id):
    if not snapshot_id: return

    checklist("Cleaning up temporary installation files")
    client = session.client("ec2")
    response = client.delete_snapshot(
       SnapshotId=snapshot_id
    )   
    checklist("Cleaning up temporary installation files","COMPLETE",True)


def read_snapshot_from_s3(session):
    client = session.client('s3')

    try:
        response = client.get_object(
            Bucket = 'qchem-qcloud',
            Key='snapshot.txt'
        )

        body = response.get('Body')
        id = body.read().decode().strip()
        return id

    except client.exceptions.NoSuchBucket as e:
        QCloudError('The qchem-qcloud bucket does not exist.')

    except client.exceptions.NoSuchKey as e:
        QCloudError('The snapshot file does not exist in the S3 bucket.')
    
    except client.exceptions.AccessDenied as e:
        QCloudError('Unable to read file snapshot.txt.')
    


def copy_snapshot(session):
    global SOURCE_SNAPSHOT
    global SOURCE_REGION

    source_region   = SOURCE_REGION
    source_snapshot = SOURCE_SNAPSHOT
    source_snapshot = read_snapshot_from_s3(session)

    if "QCLOUD_SNAPSHOT_ID" in os.environ:
       source_snapshot = os.getenv('QCLOUD_SNAPSHOT_ID')

    if "QCLOUD_SNAPSHOT_REGION" in os.environ:
       source_region = os.getenv('QCLOUD_SNAPSHOT_REGION')

    snapshot_id = None

    client = session.client("ec2")
    response = client.copy_snapshot(
       SourceRegion=source_region, 
       SourceSnapshotId=source_snapshot,
       Description='Q-Cloud {}'.format(VERSION)
    )   
    snapshot_id = response['SnapshotId']
    watch_snapshot_progress(session, snapshot_id)

    return snapshot_id


def get_snapshot_id(session):
    snapshot_id = None
    account = get_account_id(session)
    client = session.client("ec2")

    response = client.describe_snapshots(
        Filters=[
            { 'Name': 'owner-id', 'Values': [ account ] }
        ]
    )   

    for snapshot in response['Snapshots']:
        if snapshot['Description'] == 'Q-Cloud {}'.format(VERSION):
           snapshot_id = snapshot['SnapshotId']

    if not snapshot_id:
       snapshot_id = copy_snapshot(session)

    return snapshot_id


def get_account_id(session):
    client = session.client("sts")
    return client.get_caller_identity()["Account"]



class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)



class YamlDumper(yaml.SafeDumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)
        if len(self.indents) == 1:
            super().write_line_break()


 
class ConfigFile:
    def __init__(self, label):
        self.label = label
        self.config_file = "{}.config".format(label)
        self.config = { }

        if os.path.exists(self.config_file):
           if os.path.isfile(self.config_file):
               self.read(self.config_file)
           else:
               raise QCloudError("Invalid configuration file path: {}".format(self.config_file))

    def fname(self):
        return self.config_file

    def exists(self):
        return os.path.exists(self.config_file)

    def set(self, option, value):
        self.config[option] = value
        pass

    def read(self, fname):
        with open(fname, 'r') as file:
            self.config = yaml.safe_load(file)

    def dump(self):
        yaml.dump(self.config, sys.stdout, Dumper=YamlDumper, default_flow_style=False, allow_unicode=True)

    def write(self, fname = None):
        if not fname:
           fname = self.config_file
        checklist("Writing cluster configuration")
        with open(fname, 'w', encoding='utf8') as outfile:
            yaml.dump(self.config, outfile, Dumper=YamlDumper, default_flow_style=False, allow_unicode=True)
        checklist("Cluster configuration written to:", fname, True)




###############################################################################


def config_file_path():
    config_file = os.path.join(pathlib.Path.home(), ".qcloud_admin.cfg")
    return config_file


def load_config():
    path = config_file_path()
    debug('Using config file {}'.format(path))
    config = configparser.ConfigParser()
    config.read(path)
    return config


def write_config(config):
    path = config_file_path()
    with open(path, 'w') as cfg:
       config.write(cfg)
    os.chmod(path, 0o600)


def set_config_option(config, section, option, prompt):
    value = ''
    if config.has_option(section, option):
       default = config.get(section, option)
       value = input("{} [{}]: ".format(prompt, default)) or default
    else:
       value = input("{}: ".format(prompt))
    config.set(section, option, value)


def configure_session():
    config = load_config()

    if ("AWS" not in config): config.add_section("AWS")
    set_config_option(config, "AWS", "Region", "AWS Region")
    set_config_option(config, "AWS", "aws_access_key_id", "Access key")
    set_config_option(config, "AWS", "aws_secret_access_key", "Secret access key")

    write_config(config)
    return


def create_session():
    mesg = """       ***** AWS access keys have not been configured *****
         If you have not already done so, you will need to create access and
         secret keys via the Identity and Access Management (IAM) panel in the
         AWS console.  Use the --configure-aws option to add these keys."""

    config = load_config()
    if ("AWS" not in config): 
       raise QCloudError(mesg)

    session = None

    try:
       region = config.get("AWS", "region")
       access_key = config.get("AWS", "aws_access_key_id")
       secret_key = config.get("AWS", "aws_secret_access_key")

       access_masked =  '*'*12 + access_key[12:]
       secret_masked =  '*'*32 + secret_key[32:]
       debug("Using session details:")
       debug("  aws_access_key_id:     {}".format(access_masked))
       debug("  aws_secret_access_key: {}".format(secret_masked))
       debug("  region name:           {}".format(region))


       session = boto3.Session(
          aws_access_key_id = access_key, 
          aws_secret_access_key = secret_key,
          region_name = region )

       os.environ["AWS_DEFAULT_REGION"] = region
       os.environ["AWS_ACCESS_KEY_ID"] = access_key
       os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key

    except (botocore.exceptions.ClientError,
            botocore.exceptions.NoCredentialsError):
       raise QCloudError(mesg)

    return session
    

###############################################################################


def get_account_id(session):
    client = session.client("sts")
    return client.get_caller_identity()["Account"]



def create_new_keypair(session):
    checklist("Creating key pair")
    ec2_client = session.client("ec2")
    key_pairs = ec2_client.describe_key_pairs()
    key_names = [ kp['KeyName'] for kp in key_pairs['KeyPairs'] ]

    key_name = "qcloud_{}_keypair".format(session.region_name)

    count = 0
    while key_name in key_names:
        count = count + 1
        key_name = "qcloud_{}_keypair_{}".format(session.region_name,count)
    
    response = ec2_client.create_key_pair(KeyName=key_name)
    file_name = "{}.pem".format(key_name)
    with open(file_name,"w") as key_file:
        key_file.write(response['KeyMaterial'])
    os.chmod(file_name, 0o600)

    return key_name


def key_file_exists(key_name):
    key_file_name  = "{}.pem".format(key_name)
    if os.path.exists(key_file_name):
       return True
    path = Path(Path.home(), '.ssh', key_file_name)
    if path.exists():
       return True
    return False



def get_aws_keypair(session, interactive):
    checklist("Determining SSH key-pair")

    ec2_client = session.client("ec2")
    key_pairs = ec2_client.describe_key_pairs()

    key_names   = [kp['KeyName'] for kp in key_pairs['KeyPairs']]
    key_string  = "qcloud_{}_keypair".format(session.region_name)
    qcloud_keys = [k for k in key_names if key_string in k]

    for key_name in qcloud_keys:
        if key_file_exists(key_name):
           checklist("Using existing key pair:", key_name, True)
           return key_name

    checklist("Creating new key-pair")
    key_name = create_new_keypair(session)
    checklist("Using created key pair:", key_name, True)

    return key_name



def get_availability_zones(session):
    checklist("Determing availability zone")
    client = session.client('ec2')
    response = client.describe_availability_zones()
    options = [ az['ZoneName'] for az in response['AvailabilityZones'] ]
    prompt = "Select VPC availability zone:"
    az, index = pick(options, prompt, indicator='=>')
    return az



def create_vpc(session):
    checklist("Creating VPC")
    az = get_availability_zones(session)
    ec2 = session.resource("ec2")
    vpc = ec2.create_vpc(CidrBlock='172.16.0.0/16')  # 65534 IPs
    vpc.wait_until_available()
    vpc.create_tags(Tags=[{'Key': 'Name', 'Value': 'Q-Cloud VPC'}])

    checklist("Enabling DNS support")
    vpc.modify_attribute(EnableDnsSupport   = { 'Value': True })
    vpc.modify_attribute(EnableDnsHostnames = { 'Value': True })

    checklist("Creating internet gateway")
    internet_gateway = ec2.create_internet_gateway()
    vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)

    checklist("Creating route table")
    route_table = vpc.create_route_table()
    route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internet_gateway.id)

    checklist("Creating subnets")
    public = ec2.create_subnet(CidrBlock='172.16.0.0/20',  VpcId=vpc.id, 
       AvailabilityZone=az) # 4096 IPs (public)
    route_table.associate_with_subnet(SubnetId=public.id) 
    public.create_tags( Tags = [ {'Key': 'Name', 'Value': 'Q-Cloud Public'} ] )
    private = ec2.create_subnet(CidrBlock='172.16.16.0/20', VpcId=vpc.id,
        AvailabilityZone=az) # 4096 IPs (private)
    private.create_tags( Tags = [ {'Key': 'Name', 'Value': 'Q-Cloud Private'} ] )

    checklist("Adding security group")
    security_group = ec2.create_security_group(GroupName='SSH-ONLY', 
        Description='Allow only SSH traffic', VpcId=vpc.id)
    security_group.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)

    checklist("Creating VPC endpoints")
    route_table = vpc.create_route_table()
    route_table.associate_with_subnet(SubnetId=private.id) 
    ec2 = session.client('ec2')
    provider = "com.amazonaws.{}".format(session.region_name)
    
    endpoint = ec2.create_vpc_endpoint(VpcEndpointType='Gateway', VpcId=vpc.id,
        ServiceName="{}.{}".format(provider,'s3'), RouteTableIds = [ route_table.id ])
        
    endpoint = ec2.create_vpc_endpoint(VpcEndpointType='Gateway', VpcId=vpc.id,
        ServiceName="{}.{}".format(provider,'dynamodb'), RouteTableIds = [ route_table.id ])

    checklist("Created VPC:", vpc.id, True)

    return vpc.id



def get_vpc_id(session, interactive):
    checklist("Determining VPC")

    ec2_client = session.client("ec2")
    vpcs = ec2_client.describe_vpcs()

    vpc_id  = None
    vpc_ids = [ ]
    vpc_descriptions = [ ]

    for vpc in vpcs['Vpcs']:
        if vpc['State'] != "available":
            continue
        vpc_ids.append(vpc['VpcId'])
        vpc_descriptions.append('{0: <21}'.format(vpc['VpcId']))

        tags = vpc.get('Tags',[])
        for tag in tags:
            if tag['Key'] == 'Name':
                vpc_descriptions[-1] += "    " + tag['Value']
                if tag['Value'] == 'Q-Cloud VPC':
                    vpc_id = vpc['VpcId']

    vpc_descriptions.append("Create new")
    last = len(vpc_descriptions)-1
    prompt = "VPC to use:"
    if vpc_id:
       index = vpc_ids.index(vpc_id)
    else:
       index = len(vpc_descriptions)-1
    vpc_id, index = pick(vpc_descriptions, prompt, indicator='=>', default_index=index)

    if index < len(vpc_ids):
         vpc_id = vpc_ids[index]           

    if vpc_id in vpc_ids:
        checklist("Using VPC ID:", vpc_id, True)
    else:
        vpc_id = create_vpc(session)

    return vpc_id



def get_elastic_ip(session):
    ec2_client = session.client("ec2")
    checklist("Searching for available elastic IP")

    elastic_ips = ec2_client.describe_addresses()

    available_eips = []
    create_new = "Create new"
    elastic_ip = create_new

    for eip in elastic_ips['Addresses']:
        if not eip.get('AssociationId', None):
           available_eips.append(eip['PublicIp'])

    if len(available_eips) > 0:
        available_eips.append(create_new)
        prompt = "Elastic IP to use:"
        elastic_ip, index = pick(available_eips, prompt, indicator='=>', default_index=0)

    if elastic_ip == create_new:
        checklist("Allocating new elastic IP address")
        eip = ec2_client.allocate_address(Domain='vpc')
        elastic_ip = eip['PublicIp']

        response = ec2_client.create_tags(
            Resources=[
                eip['AllocationId'],
            ],
            Tags=[
                {'Key': 'Name', 'Value': 'Q-Cloud Elastic IP' },
            ],
        )

    checklist("Using elastic IP address:", elastic_ip, True)

    return elastic_ip



def get_subnet_ids(session, vpc_id):
    ec2 = session.resource("ec2")
    checklist("Searching for available subnets")

    subnets = ec2.subnets.filter( Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])


    subnet_ids = [sn.id for sn in subnets]

    if not subnet_ids:
        QCloudError("Failed to find a suitable subnet in {}".format(vpc_id))

    public_id  = subnet_ids[0]
    private_id = subnet_ids[0]

    for sn in subnets:
        tags = sn.tags[0].values()
        if 'Q-Cloud Public' in tags:
            public_id = sn.id
        elif 'Q-Cloud Private' in tags:
            private_id = sn.id

    checklist("Using public subnet:", public_id, True)

    if public_id != private_id:
        checklist("Using private subnet:", private_id, True)

    return public_id, private_id



def get_pricing_info():
    urls = [
        # Previous generation instances (JavaScript file)
        'https://a0.awsstatic.com/pricing/1/ec2/previous-generation/linux-od.min.js',
        # New generation instances (JavaScript file)
        'https://a0.awsstatic.com/pricing/1/ec2/linux-od.min.js'
    ]

    result = {}
    result['regions'] = []
    result['prices'] = defaultdict(OrderedDict)
    result['models'] = defaultdict(OrderedDict)

    for url in urls:
        response = requests.get(url)
        data     = response.content.decode('utf-8')
        match    = re.match('^.*callback\((.*?)\);?$', data, re.MULTILINE | re.DOTALL)
        data     = match.group(1)
        data     = demjson3.decode(data)
        regions  = data['config']['regions']

        for region_data in regions:
            region_name = region_data['region']

            if region_name not in result['regions']:
                result['regions'].append(region_name)

            libcloud_region_name = region_name
            instance_types = region_data['instanceTypes']

            for instance_type in instance_types:
                sizes = instance_type['sizes']
                for size in sizes:
                    price = size['valueColumns'][0]['prices']['USD']
                    if str(price).lower() == 'n/a':
                        # Price not available
                        continue

                    if size['size'] not in result['models'][libcloud_region_name]:
                        result['models'][libcloud_region_name][size['size']] = {}
                        result['models'][libcloud_region_name][size['size']]['CPU'] = int(size['vCPU'])

                        if size['ECU'] == 'variable':
                            ecu = 0 
                        else:
                            ecu = float(size['ECU'])

                        result['models'][libcloud_region_name][size['size']]['ECU'] = ecu 
                        result['models'][libcloud_region_name][size['size']]['memoryGiB'] = float(size['memoryGiB'])
                        result['models'][libcloud_region_name][size['size']]['storageGB'] = size['storageGB']

                    result['prices'][libcloud_region_name][size['size']] = float(price)

    return result

 

def filter_pricing_info(all_info, region, family):
    prices = all_info['prices'][region]
    info = {}
    instance_types = prices.keys()

    for type in instance_types:
        if 'metal' in type or not type.startswith(family): continue
        data  = all_info['models'][region][type]
        data['price'] = prices[type]
        info[type] = data

    return info    



def get_instance_type(session):
    region = session.region_name
    checklist("Gathering pricing information, this may take a while")
    
    all_info = None
    fname = "ec2_pricing_info.json"

    if os.path.exists(fname):
        with open(fname) as json_file:
            all_info = json.load(json_file)
        checklist("Pricing information read from file:", fname, True)
    else:
       all_info = get_pricing_info()
       with open(fname, "w") as json_file:
          json.dump(all_info, json_file)
       checklist("Pricing information downloaded to:", fname, True)

    families  = ['c5']
    options   = []
    all_types = []

    for family in families:
        info  = filter_pricing_info(all_info, region, family)
        types = sorted(info.keys(), key=lambda x: (info[x]['CPU'], info[x]['price']))
        all_types.extend(types)

        for type in types:
            cpus = info[type]['CPU']
            mem  = int(info[type]['memoryGiB'])
            cost = info[type]['price']
            options.append('{0: <18}  {1: >3}     {2: >4}      ${3: <5}'.format(type, cpus, mem, cost))

    checklist("Pricing information gathered for region:", region, True)
    prompt = ("Select instance type for compute nodes:\n\n"
              "   Instance Type       CPUs       GB    Hourly cost/USD")
    index = pick(options, prompt, indicator='=>', default_index=0)[1]

    return all_types[index]



def get_spot_demand():
    # Turn off spot pricing for the moment as it 
    # requires several other settings
    return ["ONDEMAND", "SPOT"][0]
    options = [ "On demand", "Spot" ]
    prompt = "Select spot pricing:"
    value, index = pick(options, prompt, indicator='=>')
    checklist("Spot pricing set to:", value, True)
    return ["ONDEMAND", "SPOT"][index]



def get_max_nodes():
    options = [ 2, 10, 25, 100]
    for i in range(len(options)):
        options[i] = "{0: >3}".format(options[i])
    prompt = "Select maximum concurrent number of compute nodes:"
    value, index = pick(options, prompt, indicator='=>',default_index=1)
    value = int(value)
    value = int(value)
    checklist("Maximum compute nodes set to:", value, True)
    return value



def get_job_volume_size():
    options = [5, 10, 20, 50]
    for i in range(len(options)):
        options[i] = "{0: >4}".format(options[i])
    prompt = "Select volume size for job files (GB):"
    value, index = pick(options, prompt, indicator='=>')
    value = int(value)
    checklist("Volume size for job file set to:", "{} GB".format(value), True)
    return value



def get_scratch_volume_size():
    options = [ 10, 20, 50, 100, 200, 500, 1000]
    for i in range(len(options)):
        options[i] = "{0: >4}".format(options[i])
    prompt = "Select volume size for scratch files (GB):"
    value, index = pick(options, prompt, indicator='=>')
    value = int(value)
    checklist("Volume size for scratch file set to:","{} GB".format(value), True)
    return value


def get_budget(email):
    options = [ 10, 20, 50, 100, 200, 500 ]
    for i in range(len(options)):
        options[i] = "{0: >3}".format(options[i])
    options.append("Custom")
    options.append("No limit")
    prompt  = "Notifications can be sent when budget limits are approached.\n"
    prompt += "Set to 'No Limit' to disable these notifications\n"
    prompt += "Select monthly budget (USD):"

    value, index = pick(options, prompt, indicator='=>')
    if value == "No limit":
       value = 0
    elif value == "Custom":
       while not value.isdigit():
           value = input("Please enter monthly budget (USD): ")

    if value:
       if not email:
           email = get_admin_email("Please enter an email address for notifications: ")
       checklist("Budget notification ","ON", True)
       checklist("Monthly budget","USD ${}".format(value), True)
    else:
       checklist("Budget notification ","OFF", True)

    return int(value), email


def configure_cluster(session, name, interactive):
    stack_name = "{}-cluster".format(name)
    config = ConfigFile(stack_name)

    key_name   = get_aws_keypair(session,interactive)
    vpc_id     = get_vpc_id(session,interactive)
    headnode_subnet, compute_subnet = get_subnet_ids(session,vpc_id)

    eip        = get_elastic_ip(session)
    node_type  = get_instance_type(session)
    on_demand  = get_spot_demand()
    max_nodes  = get_max_nodes()
    job_volume = get_job_volume_size()
    scratch    = int(get_scratch_volume_size()) + 25

    # HeadNode
    local_storage = {'RootVolume': { 'DeleteOnTermination': True, 'Encrypted': False, 'Size': 35 } }
    head_node = { 'InstanceType': "t2.micro"}
    head_node['LocalStorage'] = local_storage
    head_node['Networking']   = {'ElasticIp': eip, 'SubnetId':  headnode_subnet }
    head_node['Ssh']          = {'KeyName': key_name}
    additional_policies = [ {'Policy': 'EXECUTE_POLICY_ARN'} ]
    s3_access = [ {'BucketName': 'API_BUCKET_NAME', 'KeyName': 'jobs/*', 'EnableWriteAccess': True }]
    head_node['Iam'] = { 'AdditionalIamPolicies': additional_policies, 'S3Access': s3_access } 
    config.set('HeadNode', head_node)

    # Image
    config.set( 'Image', {'Os': 'alinux2'} )

    # Monitoring
    monitoring = { 'DetailedMonitoring': False }
    monitoring['Logs'] = {'CloudWatch': {'Enabled': True, 'RetentionInDays': 7, 'DeletionPolicy': 'Delete' }}
    monitoring['Dashboards'] = { 'CloudWatch': { 'Enabled': True } }
    config.set('Monitoring', monitoring)

    # Region
    config.set('Region', session.region_name)

    # Scheduling
    qname = node_type.replace('.','')
    s3_access2 = [ {'BucketName': 'API_BUCKET_NAME', 'KeyName': 'jobs/*', 'EnableWriteAccess': True }]
    queue = { 'Name': qname,
              'CapacityType': on_demand,
              'ComputeResources': [ { 'Name': qname, 'InstanceType': node_type, 'MinCount': 0, 
                                    'MaxCount': max_nodes} ],
              'Networking': { 'SubnetIds': [ compute_subnet ] },
              'Iam': { 'S3Access': s3_access2 }  
             }
    scheduling = {'Scheduler': 'slurm' }
    scheduling['SlurmSettings'] = { 'ScaledownIdletime': 5 }
    scheduling['SlurmQueues'] = [ queue ]
    config.set('Scheduling', scheduling)

    # SharedStorage
    qcloud = {'EbsSettings': { 'Size': 5, 'SnapshotId': 'SNAPSHOT_ID', 
              'Encrypted': False,
              'VolumeType': 'gp2'}, 
              'MountDir': '/mnt/qcloud',
              'Name': 'qcloud-ebs',
              'StorageType': 'Ebs' }

    jobs   = {'EbsSettings': { 'Size': job_volume, 'VolumeType': 'gp2'}, 
              'MountDir': '/mnt/jobs',
              'Name': 'qcloud-jobs',
              'StorageType': 'Ebs' }
    config.set('SharedStorage', [ qcloud, jobs ] )

    config.write()

    return



####################################################################################################


def get_current_costs(session):
    client = session.client('ce')

    end_date = datetime.now()
    start_date = end_date - timedelta(days=28)

    time_period = {
        'Start': start_date.strftime('%Y-%m-%d'),
        'End': end_date.strftime('%Y-%m-%d')
    }

    response = client.get_cost_and_usage(
        TimePeriod=time_period,
        Granularity='DAILY',
        Metrics=['BlendedCost']
    )

    #print(response['ResultsByTime'])

    month = 0
    week  = 0
    count = 0

    for record in response['ResultsByTime']:
        date = record['TimePeriod']['End']
        cost = float(record['Total']['BlendedCost']['Amount'])
        week  += cost
        month += cost
        cost = "${:0,.2f}".format(cost)
        print(f"{date}   {cost:>10}")
        count += 1
        if count % 7 == 0:
           week = "${:0,.2f}".format(week)
           print(f"Week total    {week:>16}")
           week = 0

    if count % 7 != 0:
           week = "${:0,.2f}".format(week)
           print(f"Week to date:  {week:>16}")
           week = 0

    month = "${:0,.2f}".format(month)
    print(f"Total  {month:>23} USD")


def bucket_is_empty(session, name):
    s3 = session.resource("s3")
    count = 0
    try:
        bucket = s3.Bucket(name)
        count = len(list(bucket.objects.filter(Prefix="jobs/")))
        #print("Bucket {} contains {} jobs".format(name,count))
    except (s3.meta.client.exceptions.NoSuchBucket, s3.meta.client.exceptions.NoSuchKey):
        #print("Bucket {} does not exist".format(name))
        pass
    return count == 0
    


def check_stack_name(name):
    ok = True
    # need to allow for -api-gateway, -users, and -cluster suffixes
    ok = ok and len(name) < 18
    ok = ok and re.match("^[a-z0-9-]*$", name)
    ok = ok and not re.match("cognito", name)
    if not ok:
       raise QCloudError("Cluster name must be fewer than 18 lowercase alphanumeric characters.")



def list_stacks(session):
    client = session.client('cloudformation')
    try:
       response = client.list_stacks() 

       for stack in response['StackSummaries']:
           status = stack['StackStatus']
           if status == "DELETE_COMPLETE": continue
           name = stack['StackName']
           time = stack['CreationTime']
           time = time.strftime("%Y/%m/%d  %H:%M:%S")
           print("{0: <30} {1: <20} {2: <30}".format(name, status, time))
    except Exception as e:
       debug(e)
       pass
    


def stack_exists(session,name):
    client = session.client('cloudformation')
    try:
        data = client.describe_stacks(StackName = name)
    except botocore.exceptions.ClientError as e:
        return False
    return True



def print_stack_status(session, stack_name):
    client = session.client('cloudformation')
    try:
       data = client.describe_stacks(StackName = stack_name)
       status = data['Stacks'][0]['StackStatus']
       if status == "CREATE_COMPLETE":
          checklist("Stack status: {}".format(stack_name), status, True)
       #elif 'ROLLBACK' in status or 'FAILED' in status:
       #   msg = data['Stacks'][0]['StackStatusReason']
       #   print("[x] Problem with stack {}".format(stack_name), msg)
       else:
          print(f"{tcol.YELLOW}[-]{tcol.ENDC} Stack status: {stack_name: <26} {status}")
    except botocore.exceptions.ClientError:
        checklist_failed(f"Stack {stack_name} does not exist")



def print_all_stack_status(session, name):
    suffixes = ["-users", "-api-gateway", "-cluster", "-budget"]
    for suffix in suffixes:
        stack_name = "{}{}".format(name,suffix)
        print_stack_status(session, stack_name)



def detach_execute_policy(session, stack_name):
    try:
        account  = get_account_id(session)
        api_name = "api-gateway".join(stack_name.split('cluster',1))
        arn = "arn:aws:iam::{}:policy/{}-execute-policy".format(account, api_name)

        cloudformation = session.resource('cloudformation') 
        stack_resource = cloudformation.StackResource(stack_name, 'RoleHeadNode')
        role   = stack_resource.physical_resource_id
        debug(arn)
        debug(role)
        client = session.client('iam')
        policy = client.get_policy(PolicyArn = arn)
        debug(policy)
        response = client.detach_role_policy(RoleName = role, PolicyArn = arn)
        debug(response)

    except botocore.exceptions.ClientError as e:
        debug("-----------------")
        debug(e)
        debug("-----------------")
        if e.response['Error']['Code'] != 'NoSuchEntity':
           raise(e)



def delete_stacks(session, stack_names):
    client = session.client('cloudformation')
    deleted = []

    for stack_name in stack_names:
        if stack_exists(session,stack_name):
           response = input("Delete stack {}? [y/N] ".format(stack_name))
           if (response == 'y' or response == 'yes'):
              if stack_name.endswith("cluster"):
                 detach_execute_policy(session, stack_name)
              client.delete_stack(StackName = stack_name)
              deleted.append(stack_name)
              if stack_name.endswith("api-gateway"):
                 api_bucket_name = get_resource_id(session, stack_name, 'ApiBucket')
                 if api_bucket_name and not bucket_is_empty(session, api_bucket_name):
                    print("Bucket {} is not empty and will NOT be deleted".format(api_bucket_name))
             
    for stack_name in deleted:
        print_stack_status(session,stack_name)



def delete_stack(session, name):
    client = session.client('cloudformation')
    stack_names = []
    
    stack_names.append("{}-budget".format(name))
    stack_names.append("{}-cluster".format(name))
    stack_names.append("{}-api-gateway".format(name))
    stack_names.append("{}-users".format(name))

    delete_stacks(session, stack_names)



def suspend_stack(session, name):
    client = session.client('cloudformation')

    deleted = []

    stack_name = "{}-cluster".format(name)
    if stack_exists(session,stack_name):
       response = input("Delete stack {}? [y/N] ".format(stack_name))
       if (response == 'y' or response == 'yes'):
          deleted.append(stack_name)
          client.delete_stack(StackName = stack_name)

    for stack_name in deleted:
        print_stack_status(session,stack_name)



def list_all_stack_resources(session, name):
    suffixes = ["-users", "-cluster", "-api-gateway", "-budget" ]
    for suffix in suffixes:
        stack_name = "{}{}".format(name,suffix)
        if stack_exists(session,stack_name):
           list_stack_resources(session, stack_name)
           print("")



def print_info(session, name, user=False):
    cloudformation = session.resource('cloudformation') 
    key_name = None
    public_ip = None

    info = []
    info.append("{:30}   {}".format('AwsRegion',session.region_name))

    try: 
        stack_name = "{}-api-gateway".format(name)
        if stack_exists(session,stack_name):
           stack = cloudformation.Stack(stack_name)
           if stack.outputs:
              for out in stack.outputs:
                  info.append("{:30}   {}".format(out['OutputKey'],out['OutputValue']))

        stack_name = "{}-users".format(name)
        if stack_exists(session,stack_name):
           #list_stack_resources(session, stack_name)
           stack = cloudformation.Stack(stack_name)
           outputs = ['CognitoUserPoolId', 'CognitoAppClientId']
           if stack.outputs:
              for out in stack.outputs:
                  if out['OutputKey'] in outputs:
                     info.append("{:30}   {}".format(out['OutputKey'], out['OutputValue']))

        stack_name = "{}-cluster".format(name)
        if stack_exists(session,stack_name):
           stack = cloudformation.Stack(stack_name)
           if stack.outputs:
              for out in stack.outputs:
                  if out['OutputKey'] == 'HeadNodeInstanceID':
                     id = out['OutputValue']
                     instance = session.resource("ec2").Instance(id)
                     info.append("{:30}   {}".format("HeadNodeInstanceId:",id))
                     info.append("{:30}   {}".format("PublicIpAddress:",
                       instance.public_ip_address))
                     info.append("{:30}   {}".format("KeyName:",instance.key_name))
                     public_ip = instance.public_ip_address
                     key_name = instance.key_name+".pem"

        stack_name = "{}-budget".format(name)
        if stack_exists(session,stack_name):
           stack = cloudformation.Stack(stack_name)
           if stack.outputs:
              for out in stack.outputs:
                  info.append("{:30}   {}".format(out['OutputKey'],out['OutputValue']))



    except Exception as e:
        pass

    if user:
       for key in ['AwsRegion', 'CognitoUserPoolId', 'CognitoAppClientId',
                   'ApiGatewayId']:
           for i in info:
               if key in i: print(i)
    else:
       print("\n".join(info))
       if (key_name and public_ip):
           cmd = "ssh -i {} -l ec2-user {}".format(key_name, public_ip)
           print("{:30}   {}".format("SSH connection:", cmd))




def get_resource_id(session, stack_name, resource_name):
    id = ''
    try:
        cloudformation = session.resource('cloudformation') 
        stack_resource = cloudformation.StackResource(stack_name,resource_name)
        id = stack_resource.physical_resource_id
    except botocore.exceptions.ClientError as e:
        #print(e)
        pass
    return id 



def list_stack_resources(session, stack_name):
    cloudformation = session.resource('cloudformation')
    client = session.client('cloudformation')

    try: 
        stacks = cloudformation.stacks.filter(StackName=stack_name)
        for stack in stacks:
            name = stack.name
            status = stack.stack_status
            print("Stack:")
            print("   {:30}   {}".format("Name",name))
            print("   {:30}   {}".format("Status",status))
            print("   {:30}   {}".format("Created",stack.creation_time))
            print("   {:30}   {}".format("ARN",stack.stack_id))
            print("   {:30}   {}".format("Description",stack.description))
            print("Tags:")
            for tag in stack.tags:
                print("   {:30}   {}".format(tag['Key'],tag['Value']))
            print("Outputs:")
            for out in stack.outputs:
                print("   {:30}   {}".format(out['OutputKey'],out['OutputValue']))
            response  = client.list_stack_resources(StackName=name)
            resources = response['StackResourceSummaries'] 
            print("Resources:")
            for r in resources:
                print("   {:30}   {}".format(r['LogicalResourceId'],r['PhysicalResourceId']))
    except:
        pass



def watch_stack_progress(session, stack_name, desired_status='CREATE_COMPLETE'):
    resource = session.resource('cloudformation')
    status = 'INITIALIZING'

    while status != desired_status:
        for i in range(128):
            checklist("Stack status: {}".format(stack_name),"{} {}".format(status,progress(i)))
            checklist_with_progress("Stack status: {}".format(stack_name),status, i)
            sleep(0.1)
        stack  = resource.Stack(stack_name)
        status = stack.stack_status
        if status == "ROLLBACK_COMPLETE":
           raise QCloudError("Failed to launch stack: {}".format(stack_name))

    checklist("Stack status: {}".format(stack_name),"{0: <35}".format(status), True)



def get_admin_email(message):
    email_validator = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    email = ""
    while not re.fullmatch(email_validator, email):
       email = input(message)

    return email


def get_userpool_arn(session, stack_name):
    arn = ''
    try:
        cloudformation = session.resource('cloudformation') 
        user_pool = cloudformation.StackResource(stack_name,'UserPool')
        region = session.region_name
        account = get_account_id(session)
        id = user_pool.physical_resource_id
        arn = "arn:aws:cognito-idp:{}:{}:userpool/{}".format(region,account,id)
    except:
       pass

    return arn


def load_template(name):
    fname = '{}.yaml'.format(name)
    #template = importlib.resources.read_text('qcloud_setup',fname)
    template = importlib.resources.files('qcloud_setup').joinpath(fname).read_text(encoding='utf-8')
    return template


def gen_iam():
    template = load_template("iam-policy")
    fname = "iam-policy.yaml"
    with open(fname, "w") as file:
         file.write(template)
    print("IAM policy written to {}".format(fname))


def update_budget(session, stack_name, monthly_amount):
    if not stack_exists(session,stack_name):
       raise QCloudError("Budget not found, update failed")

    account = get_account_id(session)
    client  = session.client('budgets')

    response = client.update_budget(
       AccountId = account,
       NewBudget = {
           'BudgetName': 'Q-Cloud budget',
           'BudgetType': 'COST',
           'TimeUnit': 'MONTHLY',
           'BudgetLimit': 
            { 'Amount': str(monthly_amount), 
              'Unit': 'USD'
            }
       }
    )

    print_stack_status(session,stack_name)



def launch_budget(session, stack_name, admin_email, monthly_amount):
    if stack_exists(session,stack_name):
       update_budget(session, stack_name, monthly_amount)
       return

    stack_body = load_template('budget')

    client = session.client('cloudformation')

    response = client.create_stack(
        StackName = stack_name,
        TemplateBody = stack_body,

        Parameters = [
            {
                'ParameterKey': 'Name',
                'ParameterValue': 'Q-Cloud budget',
            },
            {
                'ParameterKey': 'Amount',
                'ParameterValue': str(monthly_amount),
            },
            {
                'ParameterKey': 'Currency',
                'ParameterValue': 'USD',
            },
            {
                'ParameterKey': 'FirstThreshold',
                'ParameterValue': '75'
            },
            {
                'ParameterKey': 'SecondThreshold',
                'ParameterValue': '99'
            },
            {
                'ParameterKey': 'Email',
                'ParameterValue': admin_email,
            },
        ],
        TimeoutInMinutes = 10,
        Capabilities = [ 'CAPABILITY_IAM' ],
        OnFailure = 'DELETE',
        Tags = [ { 'Key': 'Name',          'Value': 'Q-Cloud Budget'},
                 { 'Key': 'QCloudVersion', 'Value': VERSION } ],
        EnableTerminationProtection=False
    )

    watch_stack_progress(session, stack_name)


def launch_cognito(session, stack_name, admin_email):
    if stack_exists(session,stack_name):
       print_stack_status(session,stack_name)
       return

    stack_body = load_template('cognito')

    client = session.client('cloudformation')

    response = client.create_stack(
        StackName = stack_name,
        TemplateBody = stack_body,
        Parameters = [
            {
                'ParameterKey': 'RootStackName',
                'ParameterValue': stack_name,
            },
            {
                'ParameterKey': 'AdminEmail',
                'ParameterValue': admin_email,
            },
            {
                'ParameterKey': 'CreateSES',
                'ParameterValue': 'false',
            },
        ],
        TimeoutInMinutes = 10,
        Capabilities = [ 'CAPABILITY_IAM' ],
        OnFailure = 'DELETE',
        Tags = [ { 'Key': 'Name',          'Value': 'Q-Cloud Cognito users'},
                 { 'Key': 'QCloudVersion', 'Value': VERSION } ],
        EnableTerminationProtection=False
    )

    watch_stack_progress(session, stack_name)



def launch_api_gateway(session, stack_name, cognitoArn):
    if stack_exists(session,stack_name):
        print_stack_status(session,stack_name)
        return

    stack_body = load_template('api-gateway')

    client = session.client('cloudformation')

    response = client.create_stack(
        StackName    = stack_name,
        TemplateBody = stack_body,
        Parameters = [
            {
                'ParameterKey': 'ApiGatewayName',
                'ParameterValue': stack_name,
            },
            {
                'ParameterKey': 'CognitoUserGroupArn',
                'ParameterValue': cognitoArn,
            },
        ],
        TimeoutInMinutes = 10,
        Capabilities = [ 'CAPABILITY_NAMED_IAM' ],
        OnFailure = 'ROLLBACK',
        Tags = [ { 'Key': 'Name',          'Value': 'Q-Cloud API Gateway'},
                 { 'Key': 'QCloudVersion', 'Value': VERSION } ],
        EnableTerminationProtection=False
    )

    watch_stack_progress(session, stack_name)



def launch_cluster(session, stack_name):
    if stack_exists(session,stack_name):
        print_stack_status(session,stack_name)
        return

    region = session.region_name
    config = ConfigFile(stack_name)
    fname  = config.fname()

    if (not config.exists()):
       raise QCloudError("Failed to find configuration file: {}".format(fname))

    checklist("Launching cluster with config file:", fname)
    cmd  = "pcluster"
    cmd += " create-cluster --cluster-configuration {}".format(fname);
    cmd += " --cluster-name {} --region {}".format(stack_name,region)

    proc = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
   
    if proc.returncode == 127:
        raise QCloudError('{}: command not found\n'.format(cmd[0]))
    elif proc.returncode != 0:
        err = demjson3.decode(proc.stdout)
        if 'message' in err.keys():
           print(err['message'])
        if 'configurationValidationErrors' in err.keys():
           msg = err['configurationValidationErrors'][0]['message']
           raise QCloudError(msg)
           
    watch_stack_progress(session, stack_name)



def launch(session, name, nocognito, admin_email):
    cognito_stack = '{}-users'.format(name)
    api_stack     = '{}-api-gateway'.format(name)
    cluster_stack = '{}-cluster'.format(name)
    budget_stack  = '{}-budget'.format(name)

    #prompt   = 'Select components to launch (use space bar to select):'
    #options  = ['Cognito Authorisation',  'API Gateway', 'Q-Cloud Cluster', ]
    #selected = pick(options, prompt, multiselect=True, min_selection_count=1)

    do_cognito = not nocognito
    do_gateway = True
    do_cluster = True 
    do_budget  = False

    if not stack_exists(session,budget_stack):
       budget, admin_email = get_budget(admin_email)
       if budget > 0 and admin_email:
          do_budget = True

    if do_cognito:
       if not admin_email:
          #admin_email = get_admin_email()
          admin_email = 'anybody@example.com'
       launch_cognito(session, cognito_stack, admin_email)

    if do_gateway:
       cognitoArn = get_userpool_arn(session, cognito_stack)
       launch_api_gateway(session, api_stack, cognitoArn)
       checklist("Updating config file with API resources")
       execute_policy_arn = get_resource_id(session, api_stack, 'ExecutePolicy')
       api_bucket_name = get_resource_id(session, api_stack, 'ApiBucket')
       update_config_file(cluster_stack, api_bucket_name, execute_policy_arn) 
       checklist("Updating config file with API resources","COMPLETE",True)

    if do_cluster:
       if not stack_exists(session,cluster_stack):
           snapshot_id = get_snapshot_id(session)
           update_config_snapshot(cluster_stack, snapshot_id)
           launch_cluster(session, cluster_stack)
           remove_snapshot(session,snapshot_id)

       update_lambda(session, cluster_stack, api_stack)
       post_launch(session, name)
       get_cluster_ip(cluster_stack)
       checklist("Q-Cloud cluster {} launch".format(name), "SUCCESS", True)

    if do_budget:
       launch_budget(session, budget_stack, admin_email, budget)


def get_cluster_ip(stack_name):
    checklist("Retrieving elastic IP address")
    config = ConfigFile(stack_name)
    fname  = config.fname()
    
    with open(fname) as file:
         text = file.read()

    ip = re.search("ElasticIp:\s*(.+)", text)
    if ip:
       checklist("Retrieving elastic IP address", ip.group(1), True)
    else:
       checklist_failed("Failed to determine elastic IP, check config file")


def update_lambda(session, cluster_stack, api_stack):
    instance_id = get_resource_id(session, cluster_stack, 'HeadNode')
    checklist("Updating config file with instance ID")
    lambda_qcloud = get_resource_id(session, api_stack, 'LambdaFunctionQCloud')
    lambda_s3submit = get_resource_id(session, api_stack, 'LambdaFunctionS3Submit')
    update_lambda_env(session, lambda_qcloud, instance_id)
    update_lambda_env(session, lambda_s3submit, instance_id)
    checklist("Updating config file with instance ID", "COMPLETE", True)
 

def update_lambda_env(session, lambda_id, instance_id):
    client = session.client("lambda")
    response = client.update_function_configuration(
        FunctionName = lambda_id,
        Environment = { 'Variables': { 'INSTANCE_ID': instance_id } }
    )


def update_config_snapshot(stack_name, snapshot_id):
    checklist("Updating config file with snapshot id")
    config = ConfigFile(stack_name)
    fname  = config.fname()
    
    with open(fname) as file:
         text = file.read()

    text = re.sub("SnapshotId:.+", "SnapshotId: {}".format(snapshot_id), text)

    with open(fname, "w") as file:
         file.write(text)

    checklist("Updating config file with snapshot", "COMPLETE", True)


def update_config_file(stack_name, api_bucket_name, execute_policy_arn):
    config = ConfigFile(stack_name)
    fname  = config.fname()
    
    with open(fname) as file:
         text = file.read()

    text = re.sub("BucketName:.+", "BucketName: {}".format(api_bucket_name), text)
    text = re.sub("- Policy:.+", "- Policy: {}".format(execute_policy_arn), text)

    with open(fname, "w") as file:
         file.write(text)





###############################################################################################


def add_user(session, name, username, email):
    if not email:
       raise QCloudError("Must specify email address with --email option")
    users = { username: email}
    create_users(session, name, users)



def add_users(session, name, users_file):
    if not os.path.exists(users_file):
       raise FileNotFoundError(users_file)

    users = {}

    with open(users_file) as file:
         lines = file.read()
         lines = lines.splitlines()
         for line in lines:
             username, email = line.split()
             users[username] = email

    create_users(session, name, users)


def list_users(session, name):
    stack_name = "{}-users".format(name)
    if not stack_exists(session,stack_name):
       raise QCloudError("Could not find stack {}".format(stack_name))

    pool_id = get_resource_id(session, stack_name, "UserPool")
    cognito = session.client('cognito-idp')

    response = cognito.list_users(UserPoolId = pool_id)
    if 'Users' in response:
       
       print("{0: <12}  {1: <20}  {2: <21}  {3: <40}".format('User name', 'Created', 'Status', 'Email' ))
       print("{0: <12}  {1: <20}  {2: <21}  {3: <40}".format('-'*12, '-'*20, '-'*21, '-'*30))
       users = response['Users'] 
       for user in users:
           name    = user['Username']
           status  = user['UserStatus']
           created = user['UserCreateDate']
           created = created.strftime("%Y/%m/%d  %H:%M:%S")
           attrib  = user['Attributes']
           for att in attrib:
               if att['Name'] == 'email': 
                  email = att['Value']
           print("{0: <12}  {1: <20}  {2: <21}  {3: <40}".format(name, created, status, email))


def create_users(session, name, users):
    stack_name = "{}-users".format(name)
    if not stack_exists(session,stack_name):
       raise QCloudError("Could not find stack {}".format(stack_name))

    pool_id = get_resource_id(session, stack_name, "UserPool")
    cognito = session.client('cognito-idp')

    for username, email in users.items():
        checklist("Adding user:", username)
        try:
            response = cognito.admin_create_user(
                UserPoolId = pool_id,
                Username = username,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name':  'email_verified',
                        'Value': 'true' 
                    },
                ],
                ForceAliasCreation = False,
                DesiredDeliveryMediums = [ 'EMAIL' ]
            )
            checklist("Added user:", username, True)

        except botocore.exceptions.ClientError as e:
           if e.response['Error']['Code'] == 'UsernameExistsException':
              checklist("User already exists:", username, True)
           else:
              raise e



def confirm_user(session, username, password, user_pool_id, app_client_id):
    client = session.client('cognito-idp')
    resp = client.admin_confirm_sign_up(
        UserPoolId=user_pool_id,
        Username=username
    )

    print("User successfully created.")



def authenticate_and_get_token(username, password, user_pool_id, app_client_id):
    client = boto3.client('cognito-idp')

    resp = client.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=app_client_id,
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password
        }
    )

    print("Log in success")
    print("Access token:", resp['AuthenticationResult']['AccessToken'])
    print("ID token:", resp['AuthenticationResult']['IdToken'])



###############################################################################################

def update_license_file(license_file, private_ip, public_ip):
    server_line = "SERVER {} AMZN_EIP={}\n".format(private_ip, public_ip)
    with open(license_file) as file:

         text = file.read()
         if "SERVER" in text:
            lines = text.splitlines(True)
            text = ''
            for line in lines:
                if "SERVER" in line:
                   line = server_line
                text += line
         else:
            text = server_line + text
        
    with open(license_file, "w") as file:
         file.write(text)



def install_license_key(session, name, activation_code):
    ssh_client = ssh_connection(session, name)

    cmd = "/mnt/qcloud/bin/install_license {}".format(activation_code)

    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
    ssh_stdout.channel.recv_exit_status()
    lines = ssh_stdout.readlines()
    debug(lines)

    services = [ "QChemLicensingService"]
    for service in services:
        sleep(1)
        checklist("Checking service {}".format(service))
        cmd = "sudo systemctl is-active {}".format(service)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
        ssh_stdout.channel.recv_exit_status()
        lines = ssh_stdout.readlines()
        status = "failed"
        if len(lines) == 1:
           status = lines[0].strip()

        if status == "failed":
           checklist_failed(f"Checking service {service}", status)
           cmd = "tail -1 /mnt/qcloud/log/license_renewal.log"
           ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
           ssh_stdout.channel.recv_exit_status()
           lines = ssh_stdout.readlines()
           if len(lines) > 0:
              line = lines[0][28:]
              line = line.strip() 
              print(line)
        else:
           checklist("Checking service {}".format(service), status, True)



def post_launch(session, name):
    checklist("Performing post launch configuration");
    ssh_client = ssh_connection(session, name)
    checklist("Updating packages")
    cmd = "/mnt/qcloud/bin/post_install"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
    ssh_stdout.channel.recv_exit_status()
    lines = ssh_stdout.readlines()
    debug(lines)

    checklist("Performing post launch configuration","COMPLETE", True);


def ssh_connection(session, name):
    checklist("Getting stack information")
    cloudformation = session.resource('cloudformation') 
    stack_name = "{}-cluster".format(name)

    if not stack_exists(session,stack_name):
       raise QCloudError("Could not find stack {}".format(stack_name))
  
    key_name  = None
    public_ip = None 
    stack = cloudformation.Stack(stack_name)

    if not stack.outputs:
       raise QCloudError("Unable to connect to head node")
       
    for out in stack.outputs:
        if out['OutputKey'] == 'HeadNodeInstanceID':
           id = out['OutputValue']
           instance = session.resource("ec2").Instance(id)
           public_ip = instance.public_ip_address
           key_name = "{}.pem".format(instance.key_name)

    if (not key_name):
       raise QCloudError("Could not obtain ssh key")

    if (not public_ip):
       raise QCloudError("Could not obtain public IP address of head node")

    if not os.path.exists(key_name):
       path = Path(Path.home(), '.ssh', key_name)
       if not path.exists():
          raise QCloudError(f"Could not find key file {key_name}")
       key_name = path

    key = paramiko.RSAKey.from_private_key_file(key_name)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=public_ip, username='ec2-user', pkey=key)
    checklist("Connection established", "", True)

    return ssh_client

 

def execute_slurm(session, name, args):
    cmd = " ".join(args)
    ssh_client = ssh_connection(session, name)
    checklist("Executing command")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
    ssh_stdout.channel.recv_exit_status()
    lines = ssh_stdout.readlines()
    for line in lines: print(line)



def open_shell(session, name):
    connection = ssh_connection(session, name)
    oldtty_attrs = termios.tcgetattr(sys.stdin)
    channel = connection.invoke_shell()

    def resize_pty():
        tty_height, tty_width = \
                subprocess.check_output(['stty', 'size']).split()

        try:
            channel.resize_pty(width=int(tty_width), height=int(tty_height))
        except paramiko.ssh_exception.SSHException:
            pass

    try:
        stdin_fileno = sys.stdin.fileno()
        tty.setraw(stdin_fileno)
        tty.setcbreak(stdin_fileno)
        channel.settimeout(0.0)
        is_alive = True

        while is_alive:
            resize_pty()
            read_ready, write_ready, exception_list = \
                    select.select([channel, sys.stdin], [], [])

            if channel in read_ready:
                try:
                    out = channel.recv(1024).decode()

                    if len(out) == 0:
                        is_alive = False
                    else:
                        print(out, end='')
                        sys.stdout.flush()

                except socket.timeout:
                    pass

            if sys.stdin in read_ready and is_alive:
                char = os.read(stdin_fileno, 1)
                if len(char) == 0:
                    is_alive = False
                else:
                    channel.send(char)

        channel.shutdown(2)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, oldtty_attrs)
        print('Connection to %s closed.' % name)



def get_log_group_names(client, name):
    groupNames = []

    groups = client.describe_log_groups(
        logGroupNamePrefix = '/aws/lambda/{}'.format(name)
    )
    for group in groups['logGroups']:
        groupNames.append(group['logGroupName'])

    groups = client.describe_log_groups(
        logGroupNamePrefix = 'API-Gateway-Execution-Logs'.format(name)
    )
    for group in groups['logGroups']:
        groupNames.append(group['logGroupName'])

    prompt   = 'Select logs to retreive (use space bar to select):'
    selected = pick(groupNames, prompt, multiselect=True, min_selection_count=1)

    groupNames = []
    for s in selected:
        groupNames.append(s[0])

    return groupNames



def print_logs(session, name, log_duration):
    client = session.client('logs')

    now = int(1000*datetime.now().timestamp()) 
    start_time = 0
    log_duration = int(log_duration)

    if log_duration == 0:
       start_time = 0
    else:
       start_time = now - log_duration * 60 * 1000 # convert from min to msec

    log_group_names = get_log_group_names(client, name);

    for group in log_group_names:
        all_streams = []
        stream_batch = client.describe_log_streams(logGroupName = group)
        all_streams += stream_batch['logStreams']

        while 'nextToken' in stream_batch:
            stream_batch = client.describe_log_streams(
                logGroupName = group,
                nextToken = stream_batch['nextToken']
            )
            all_streams += stream_batch['logStreams']

        stream_names = [ stream['logStreamName'] for stream in all_streams]

        fname = group + "_" + str(time()) + "_log.txt"
        checklist("Downloading logs for group", group)
        fname = fname.replace('/','_')
        out_file = open(fname, 'w')
        for stream in stream_names:
            logs_batch = client.get_log_events(
                logGroupName  = group, 
                logStreamName = stream,
                startTime     = start_time,
            )

            for event in logs_batch['events']:
                event.update({'group': group, 'stream': stream })
                out_file.write(json.dumps(event) + '\n')

                while 'nextToken' in logs_batch:
                    logs_batch = client.get_log_events(
                        logGroupName  = group, 
                        logStreamName = stream, 
                        nextToken     = logs_batch['nextToken'],
                        startTime     = start_time,
                    )
                    for event in logs_batch['events']:
                        event.update({'group': group_name, 'stream':stream })
                        out_file.write(json.dumps(event) + '\n')

        checklist("Logs downloaded to", fname, True)



def debug_api(session, name):
    client = session.client("apigateway")
    api_stack = "{}-api-gateway".format(name)
    api_gatewayId = get_resource_id(session, api_stack, 'ApiGatewayRestApi')
    print("{0: <24} {1}".format('ApiGateway ID', api_gatewayId))

    response = client.get_deployments(
       restApiId = api_gatewayId
    )

    for item in response["items"]:
        print("{0: <24} {1}   {2}".format("Deployment ID", item["id"], item["createdDate"]))

    response = client.get_authorizers(
       restApiId = api_gatewayId
    )

    for item in response["items"]:
        print("{0: <24} {1} ".format("Authorizer ID", item["id"]))
        print("{0: <24} {1} ".format("Authorizer Name", item["name"]))
        print("{0: <24} {1} ".format("Authorizer Type", item["type"]))
        print("{0: <24} {1} ".format("Authorizer Provider", item["providerARNs"]))
        print("{0: <24} {1} ".format("Authorizer Source", item["identitySource"]))

    client = session.client('cognito-idp')

    


    


###############################################################################################


def main():
    try: 
        parser = MyParser();

        parser.add_argument("--configure-aws", dest="config_aws", action='store_true',
            help="configure AWS Q-Cloud admin account.")

        parser.add_argument("--gen-policy", dest="gen_iam", action='store_true',
            help="create the IAM policy template")

        parser.add_argument("--configure", dest="config", action='store_true',
            help="creates a cluster configuration file")

        parser.add_argument("--name", dest="cluster_name", default="qcloud", 
            help="specifies the cluster name name (default=qcloud)")

        parser.add_argument("--launch", dest="launch", action='store_true',
            help="launches a cluster with the specified name (default=qcloud)")

        parser.add_argument("--no-cognito", dest="nocognito", action='store_true',
            help="disable cognito stack for managing users")

        parser.add_argument("--budget", dest="budget", action='store_true',
            help="add budget notifications")

        parser.add_argument("--activation-key", dest="license_key", 
            help="specifies the activation key for the Q-Chem license")

        parser.add_argument("--status", dest="status", action='store_true',
            help="report stack statuses")

        parser.add_argument("--resources", dest="resources", action='store_true',
            help="full list of stack resources")

        parser.add_argument("--info", dest="info", action='store_true',
            help="summary of stack resources")

        parser.add_argument("--set-budget", dest="budget", default=-1,
            help="set the monthly budget for notifications")

        parser.add_argument("--costs", dest="costs", action='store_true',
            help="summary of costs for the previous week")

        parser.add_argument("--userinfo", dest="userinfo", action='store_true',
            help="stack parameters required by users")

        parser.add_argument("--list", dest="list", action='store_true',
            help="list all cloudformation stacks")

        parser.add_argument("--adduser", dest="adduser",
            help="add user to the cognito user pool")

        parser.add_argument("--addusers", dest="users_file", 
            help="add multiple users to the cognito user pool")

        parser.add_argument("--listusers", dest="listusers", action='store_true',
            help="list all users in the cognito user pool")

        parser.add_argument("--email", dest="email",
            help="specify the user's email address")

        parser.add_argument("--logs", dest="logs", action='store_true',
            help="request Cloudwatch logs")

        parser.add_argument("--duration", dest="log_duration", default=5, 
            help="specifies the duration for reporting logs (default = 5min)")

        parser.add_argument("--suspend", dest="suspend", action='store_true',
            help="suspend the compute stack")

        parser.add_argument("--delete", dest="delete", action='store_true',
            help="delete stack(s)")

        parser.add_argument("--debug", dest="debug", action='store_true',
            help="add additional debug printing")

        parser.add_argument("--slurm", dest="slurm", action='store_true',
            help="execute given slurm commnad")

        parser.add_argument("--shell", dest="shell", action='store_true',
            help="open shell connection to the head node")


        args, extra_args = parser.parse_known_args()

        if args.debug:
           global DEBUG
           DEBUG = True

        if args.config_aws:
            configure_session()
            exit(0)

        if args.gen_iam:
            gen_iam()
            exit(0)

        session = create_session() 
        interactive = True
        name = args.cluster_name

        check_stack_name(name)

        if args.budget and int(args.budget) >= 0:
           print("args " , args.budget)
           budget_stack = f"{name}-budget"
           if stack_exists(session, budget_stack):
              update_budget(session, budget_stack, args.budget)
              exit(0)

           email = args.email
           if not email:
              email = get_admin_email("Please enter an email address for notifications: ")

           launch_budget(session, budget_stack, email, args.budget)
           exit(0)

        if args.launch:
           config = ConfigFile("{}-cluster".format(name))
           if not config.exists(): args.config = True

        if len(sys.argv)==1:
           parser.print_help(sys.stderr)
           sys.exit(1)

        if args.config:
            configure_cluster(session, name, interactive)

        if args.launch:
            launch(session, name, args.nocognito, args.email)
            if args.license_key:
               install_license_key(session, name, args.license_key)

        elif args.status:
            print_all_stack_status(session, name)

        elif args.delete:
            if extra_args:
               delete_stacks(session, extra_args)
            else:
               delete_stack(session, name)

        elif args.suspend:
            suspend_stack(session, name)

        elif args.resources:
            list_all_stack_resources(session, name)

        elif args.info:
            print_info(session,name)

        elif args.userinfo:
            print_info(session,name,True)

        elif args.adduser:
            add_user(session, name, args.adduser, args.email)

        elif args.users_file:
            add_users(session, name, args.users_file)

        elif args.listusers:
            list_users(session, name) 

        elif args.license_key:
            install_license_key(session, name, args.license_key)

        elif args.slurm:
            execute_slurm(session, name, extra_args)

        elif args.shell:
            open_shell(session, name)

        elif args.logs:
            print_logs(session, name, args.log_duration)

        elif args.list:
            list_stacks(session)

        elif args.debug:
            debug_api(session, name)

        elif args.costs:
            get_current_costs(session)

        elif args.config:
            pass

        else:
           print("ERROR: Invalid option specified")
           parser.print_help(sys.stderr)


    except KeyboardInterrupt:
        print("\n")
        pass

    except QCloudError as e:
        print(f"\n{tcol.RED}ERROR: {e}{tcol.ENDC}")

    except FileNotFoundError as e:
        print(e)

    except botocore.exceptions.ClientError as e:
        print(e)

    except botocore.exceptions.ProfileNotFound as e:
        print(e)

    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
