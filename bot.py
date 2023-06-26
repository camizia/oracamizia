availabilityDomains = ["jOgN:EU-PARIS-1-AD-1"]
displayName = 'ubcame'
compartmentId = 'ocid1.tenancy.oc1..aaaaaaaaiit4g67sivbh65tvg27snfk3cfloqeczex466qz53rnlhj24c2aq'
subnetId = 'ocid1.subnet.oc1.eu-paris-1.aaaaaaaaznelum6oaq2xzqttjq3r7kggvbq263lihinkq4r2hawrthsbclha'
ssh_authorized_keys = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8ABKujOHMX7U3aJiz0FbEXSD/ngn0oJKqK+WreVK2JX7Y0MjhHWcP0qS9Ch7FHErVy+E/fOTiEwG/h/F+yI2AjdN+VHXKfSCxOeUAYQAKn7Vjg39XEik1umN7Bl1NRzvzloL/3PaROAReEakn3kTnciGJLiByiZHV/KogaVP+lSJXEFpuLXb60GjTqUiEcJiY6DkKvxLKR+uWXEg+f+obDWeCYQ7WmAFbHT1vn3MUhGZsp7iPHLj/GkmWDIJYvO+0c2lcC2SKHW/ecjPUU9600oWagXWGaExiUm3NfSlhJ9J+aMVXcetAa1Zs9FLFswoAzJORKKIgBCekvsDD00DB rsa-key-20230626"

imageId = "ocid1.image.oc1.eu-paris-1.aaaaaaaa4cnikvo2squudozlr65bp5ndutdyadj5ewebvccubqvfd4kabyrq"
boot_volume_size_in_gbs=50
boot_volume_id="xxxx"

bot_token = "xxxx"
uid = "xxxx"

ocpus = 4
memory_in_gbs = 24

import oci
import logging
import time
import sys
import telebot

bot = telebot.TeleBot(bot_token)

LOG_FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("oci.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("#####################################################")
logging.info("Script to spawn VM.Standard.A1.Flex instance")


message = f'Start spawning instance VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB'
logging.info(message)

logging.info("Loading OCI config")
config = oci.config.from_file(file_location="./config")

logging.info("Initialize service client with default config file")
to_launch_instance = oci.core.ComputeClient(config)


message = f"Instance to create: VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB"
logging.info(message)

logging.info("Check current instances in account")
logging.info(
    "Note: Free upto 4xVM.Standard.A1.Flex instance, total of 4 ocpus and 24 GB of memory")
current_instance = to_launch_instance.list_instances(
    compartment_id=compartmentId)
response = current_instance.data

total_ocpus = total_memory = _A1_Flex = 0
instance_names = []
if response:
    logging.info(f"{len(response)} instance(s) found!")
    for instance in response:
        logging.info(f"{instance.display_name} - {instance.shape} - {int(instance.shape_config.ocpus)} ocpu(s) - {instance.shape_config.memory_in_gbs} GB(s) | State: {instance.lifecycle_state}")
        instance_names.append(instance.display_name)
        if instance.shape == "VM.Standard.A1.Flex" and instance.lifecycle_state not in ("TERMINATING", "TERMINATED"):
            _A1_Flex += 1
            total_ocpus += int(instance.shape_config.ocpus)
            total_memory += int(instance.shape_config.memory_in_gbs)

    message = f"Current: {_A1_Flex} active VM.Standard.A1.Flex instance(s) (including RUNNING OR STOPPED)"
    logging.info(message)
else:
    logging.info(f"No instance(s) found!")


message = f"Total ocpus: {total_ocpus} - Total memory: {total_memory} (GB) || Free {4-total_ocpus} ocpus - Free memory: {24-total_memory} (GB)"
logging.info(message)

if total_ocpus + ocpus > 4 or total_memory + memory_in_gbs > 24:
    message = "Total maximum resource exceed free tier limit (Over 4 ocpus/24GB total). **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

if displayName in instance_names:
    message = f"Duplicate display name: >>>{displayName}<<< Change this! **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

message = f"Precheck pass! Create new instance VM.Standard.A1.Flex: {ocpus} opus - {memory_in_gbs} GB"
logging.info(message)

wait_s_for_retry = 10

if imageId!="xxxx":
	if boot_volume_size_in_gbs=="xxxx":
		op=oci.core.models.InstanceSourceViaImageDetails(source_type="image", image_id=imageId)
	else:
		op=oci.core.models.InstanceSourceViaImageDetails(source_type="image", image_id=imageId,boot_volume_size_in_gbs=boot_volume_size_in_gbs)
		
if boot_volume_id!="xxxx":
	op=oci.core.models.InstanceSourceViaBootVolumeDetails(source_type="bootVolume", boot_volume_id=boot_volume_id)

while True:
    for availabilityDomain in availabilityDomains:
        instance_detail = oci.core.models.LaunchInstanceDetails(
    metadata={
        "ssh_authorized_keys": ssh_authorized_keys
    },
    availability_domain=availabilityDomain,
    shape='VM.Standard.A1.Flex',
    compartment_id=compartmentId,
    display_name=displayName,
    source_details=op,
    create_vnic_details=oci.core.models.CreateVnicDetails(
        assign_public_ip=False, subnet_id=subnetId, assign_private_dns_record=True),
    agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
        is_monitoring_disabled=False,
        is_management_disabled=False,
        plugins_config=[oci.core.models.InstanceAgentPluginConfigDetails(
            name='Vulnerability Scanning', desired_state='DISABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Compute Instance Monitoring', desired_state='ENABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Bastion', desired_state='DISABLED')]
    ),
    defined_tags={},
    freeform_tags={},
    instance_options=oci.core.models.InstanceOptions(
        are_legacy_imds_endpoints_disabled=False),
    availability_config=oci.core.models.LaunchInstanceAvailabilityConfigDetails(
        recovery_action="RESTORE_INSTANCE"),
    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=ocpus, memory_in_gbs=memory_in_gbs)
)
    try:
        to_launch_instance.launch_instance(instance_detail)
        message = 'VPS is created successfully! Watch video to get public ip address for your VPS'
        logging.info(message)
        if bot_token!="xxxx" and uid!="xxxx":
        	bot.send_message(uid, message)
        sys.exit()
    except oci.exceptions.ServiceError as e:
        if e.status == 500:
            message = f"{e.message}. Retrying after {wait_s_for_retry} seconds"
            logging.info(message)
            if bot_token!="xxxx" and uid!="xxxx":
            	bot.send_message(uid, message)
            time.sleep(wait_s_for_retry)
        elif e.status == 429:
            wait_s_for_retry=wait_s_for_retry+1
            message = f'"Too Many Requests" error detected. Increased retry time by 1 second. Retrying after {wait_s_for_retry} seconds'
            logging.info(message)
            if bot_token!="xxxx" and uid!="xxxx":
            	bot.send_message(uid, message)
            time.sleep(wait_s_for_retry)
        else:
            logging.info(f"{e}")
            logging.info("Error detected. Stopping script. Check your bot.py file, cofig file and oci_private_key.pem file. If you can't fix error, contact me")
            sys.exit()
    except Exception as e:
        logging.info(f"{e}")
        logging.info("Error detected. Stopping script. Check your bot.py file, cofig file and oci_private_key.pem file. If you can't fix error, contact me")
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()