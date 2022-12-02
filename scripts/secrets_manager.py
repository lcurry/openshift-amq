import requests
import secrets
import argparse

# The aim of this script is to provide basic secrets management using gitlab variables so that no password is ever stored in our builds
# This script will take the name of the variable and assign a randomly generated value.
# If the delete flag is passed then the variable will be deleted from the project

parser = argparse.ArgumentParser(description='Simple manager for Gitlab Variables')
parser.add_argument('--create',help="Create a new variable",action="store_true")
parser.add_argument('--delete',help="Remove a variable",action="store_true")
parser.add_argument('--get',help="Get a variable",action="store_true")
parser.add_argument('--varname',help="Variable name")
parser.add_argument('--project',help= 'id of the project',default='79139')
args = parser.parse_args()

def get_gitlab_var(token,project,variable):
    headers = {
        "PRIVATE-TOKEN": token
    }
    url ="https://gitlab.us.lmco.com/api/v4/projects/"+project+"/variables/"+variable
    try:
        req= requests.get(url,headers=headers)
        print(req.content)
        return 
    except Exception as e:
        print(e) 
        return 1

def create_gitlab_var(token,project,variable,value):
    headers = {
        "PRIVATE-TOKEN": token
    }
    data = {
        "key": variable,
        "value": value
    }
    url ="https://gitlab.us.lmco.com/api/v4/projects/"+project+"/variables"
    
    try:
        req = requests.post(url,headers=headers, data=data)
        print(req.content)
        return 
    except Exception as e:
        print(e) 
        return 1
def delete_gitlab_var(token,project,variable):
    headers = {
        "PRIVATE-TOKEN": token
    }
    url ="https://gitlab.us.lmco.com/api/v4/projects/"+project+"/variables/"+variable
    try:
        req= requests.delete(url,headers=headers)
        print(req.content)
        return req.content
    except Exception as e:
        print(e) 
        return 1

password=secrets.token_hex()
token= 'jbP9yzir2E3CyJ5eNSpH'
# Set the password so the cert process uses it to download the key
if args.create :
    create_gitlab_var(token,args.project,args.varname,password)

if args.delete :
    delete_gitlab_var(token,args.project,args.varname)

if args.get  :
    get_gitlab_var(token,args.project,args.varname)