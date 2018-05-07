#-*- coding: utf-8 -*-
import datetime
import logging
import netmiko
from netmiko import ConnectHandler
import getpass
import sys
import textfsm
from tabulate import tabulate





# **Определение переменных**
PASSWORD = "pas"
USER = "admin"
interface = "Fa0/19"
SHOW = "show interface %s status " % interface
template = 'descr.template'
logging.basicConfig(filename='main.log', level=logging.INFO)


 
with open('ip_list', 'r') as ip_list:  # Open list with mpls devices
    for ip in ip_list:
        IP = ip.rstrip()
        #print "connection to %s" % IP
        DEVICE_PARAMS = {'device_type': 'cisco_ios',
            'ip': IP,
            'username': USER,
            'password': PASSWORD}
        try:  # Try ssh at first
            ssh = ConnectHandler(**DEVICE_PARAMS)
            result = ssh.send_command(SHOW)
            #logging.info("%s %s %s" % (datetime.datetime.now(), IP, result))
            with open(IP, 'w') as dest:
                for line in result:
                    dest.write(line)                
        except netmiko.ssh_exception.NetMikoAuthenticationException:
            logging.info("host %s have wrong auth param" % IP)            
        except netmiko.ssh_exception.NetMikoTimeoutException:  #If ssh fail, telnet then
            print "host %s don't have ssh" % IP
            DEVICE_PARAMS = {'device_type': 'cisco_ios_telnet',
                'ip': IP,
                'username': USER,
                'password': PASSWORD}
            try:
                telnet = ConnectHandler(**DEVICE_PARAMS)
                result = telnet.send_command(SHOW)
                with open(IP, 'w') as dest:
                    for line in result:
                        dest.write(line)
                #logging.info("%s %s %s" % (datetime.datetime.now(), IP, result))
            except  netmiko.ssh_exception.NetMikoAuthenticationException:  # if no radius configured
                logging.info("host %s have wrong auth param, or problem with radius configuration" % IP)
        output_file = IP   # File with output
        f = open(template)  # File with template
        output = open(output_file).read()
        re_table = textfsm.TextFSM(f)
        header = re_table.header
        result_parse = re_table.ParseText(output)
        flat_list = [item for sublist in result_parse for item in sublist]  # Mking flat list
        int_desc=dict(zip(header,flat_list))  # Create dict from two lists
        print int_desc['Port']
        print int_desc['Name']        
         
