import requests
import os
import time
import base64
import argparse
parser = argparse.ArgumentParser(description='Simple manager for Gitlab Variables')
parser.add_argument('--password',help="Variable name")
parser.add_argument('--project',help= 'id of the project',default='79139')
args = parser.parse_args()
# This script will require the following environment variables to be set in your system:
# VENAFI_PASSWORD
# VENAFI_USER 
# PROJECT_NAME
def login_to_venafi():
    print("Logging in to Venafi")
    data ={
    "Username": os.getenv('VENAFI_USER'),
    "Password" : os.getenv('VENAFI_PASSWORD')
    }
    url = 'https://certm.global.lmco.com/vedsdk/Authorize/'
    requests.post(url, json=data, verify="./amq-broker/lm_ca.pem")
    try:
        apikey = requests.post(url, json=data, verify="./amq-broker/lm_ca.pem")
        print("Success")
        return apikey.json()["APIKey"]
    except:
        print("Fail")
        exit(1)

def create_cert(apikey,app_name,policydn,subject,namespace,cert_type):
    print("Creating Certificate")    
    url = 'https://certm.global.lmco.com/vedsdk/Certificates/Request'
    apiheader = {
        "X-Venafi-Api-Key": apikey
    }
    data = { 
        "CertificateType": "Server",
        "CreatedBy": "Gitlab",
        "PolicyDN": policydn,
        "Subject": subject,
        "SubjectAltNames": [
        {
        "TypeName": 2,
        "Name": app_name+"-"+cert_type+"-0-svc-rte-"+namespace+".apps.ocp-uge1-dev.ecs.us.lmco.com"
        },
        {
        "TypeName": 2,
        "Name": app_name+"-"+cert_type+"-0-svc"
        },
        {
        "TypeName": 2,
        "Name": app_name+"-"+cert_type+"-0-svc."+namespace+".svc"
        },
        {
        "TypeName": 2,
        "Name": app_name+"-"+cert_type+"-0-svc."+namespace+".svc.cluster.local"
        }
]
    }
    try:
        created_cert = requests.post(url,json=data,headers=apiheader, verify="./amq-broker/lm_ca.pem")
        cert_dn = created_cert.json()['CertificateDN']
        print("Success")
        return cert_dn
    except Exception as e:
        print(e)
        exit(1)

def download_cert(apikey,cert_dn,filename,password):
    print("Downloading Certificate: " + filename)

    header = {
        "X-Venafi-Api-Key" : apikey
    }
    data = { 
        "CertificateDN": cert_dn,
        "Format": "PKCS #12",
        "IncludePrivateKey": "true",
        "KeystorePassword": password,
        "Password": password
    }
    url= 'https://certm.global.lmco.com/vedsdk/Certificates/Retrieve'
    try:
        certdata = requests.post(url, json=data, headers=header, verify="./amq-broker/lm_ca.pem")
        certificate = base64.b64decode(certdata.json()["CertificateData"])
        with open("./certs/"+filename, 'wb') as f:
            f.write(certificate)
        print("Success")        
        return
    except Exception as e:
        print(e)    
        exit(1)


apikey = login_to_venafi()

policydn="\\VED\\Policy\\Certificates\\Internal\\EBS-TO\\Infrastructure\\Enter Storage & App Infrastructure\\App IF\\"
projectname=os.getenv('PROJECT_NAME')
app_name= os.getenv('APP_NAME')
cert_dn = policydn+app_name

#Create and download the broker certificate
filename="amq-"+app_name+".pfx"
cert_type = "amq"
create_cert(apikey,app_name,policydn,app_name,projectname,cert_type)
# We should wait a bit so the cert is ready to download, if we try too fast the download throws a 500
time.sleep(30)
download_cert(apikey,cert_dn,filename,args.password)

# Create and download the web certificate
cert_type = "wconsj"
create_cert(apikey,app_name,policydn,app_name,projectname,cert_type)
# We should wait a bit so the cert is ready to download, if we try too fast the download throws a 500
time.sleep(30)
filename="web-"+app_name+".pfx"
download_cert(apikey,cert_dn,filename,args.password)