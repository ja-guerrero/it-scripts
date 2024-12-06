#This Script is a Lambda Function to create users. This can be uploaded in Lambda and Called Asycrhonsly from Zapier, Make, IT HelpDesk Automations
#The Main benefit of this are for Comapnies that do not have an HRIS System or One that is intergratable with Okta as a profile Source

import requests
import os
import logging

# Initialize you log configuration using the base class
logging.basicConfig(level = logging.INFO)

# Retrieve the logger instance
logger = logging.getLogger()

# Log your output to the retrieved logger instance

#Retrieve API Oktne and Domain from AWS Lambda Environment Variables
OKTA_API_BASE_URL = os.environ["OKTA_URL"]
OKTA_API_TOKEN = os.environ["OKTA_TOKEN"]
DOMAIN = os.environ["DOMAIN"]

#Replace &amp with & for Formatting errors
def replace_ampersand(text):
    return text.replace("&amp;", "&")

def check_email_availability(email):
    url = f"{OKTA_API_BASE_URL}/users/{email}"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f"SSWS {OKTA_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 404
    
def declare_email(name):
    names = name.split(" ")
    names =  [x for x in names if x]
    print(names)
    email = names[0][0] + names[-1] + DOMAIN #Update with Org's Domain
    return email.lower()

#Find if Email Already exists and if not find an available email by adding a number to the email
def find_available_email(email):
    if check_email_availability(email):
        return email
    
    count = 1
    while True:
        prefix = email.split("@")[0]
        domain = email.split("@")[1]
        new_email = f"{prefix}{count}@{domain}"
        if check_email_availability(new_email):
            return new_email
        count += 1
    
#Define Department, Division and Sub Department
def getDepartment(evntDept:str):
    #Split the Department, Division and Sub Department from Single Line Field
    #Change to Match the format this information comes in as
    if len(evntDept.split("-")) > 1:
        division = replace_ampersand(evntDept.split("-")[0].strip())
        department= replace_ampersand(evntDept.split("-")[1].strip())
    else:
        division = department = evntDept  
    if len(evntDept.split("-")) > 2:
        sub_department = replace_ampersand(evntDept.split("-")[2].strip())
    
  
    return division, department, sub_department

#Create Okta Account using Okta API
def createOktaAccount(event):
    url = f"{OKTA_API_BASE_URL}/users?activate=true&sendEmail=false&nextLogin=true"
    email = declare_email(event["name"])
    available_email = find_available_email(email)
    managerEmail = event["memail"] #Manager Email
    division, department, sub_division = getDepartment(event["department"])

    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f"SSWS {OKTA_API_TOKEN}"
    }
    
    user_attributes = {
    'profile': {
        'firstName': event["name"].split(" ")[0],
        'lastName': event["name"].split(" ")[1],
        'email': available_email,
        'login': available_email,
        'manager': event["manager"],
        'managerId': managerEmail,
        'title': event["title"],
        'secondEmail': event["pemail"],
        'division': division,
        'department': department,
        'subDepartment': sub_division,
        "startDate": event["startdate"],
        "officeID": event["location"]
        }
    }
    response = requests.post(url, json=user_attributes,headers=headers)
    print(response.json())
    return {"user": response.json(), "status_code": response.status_code}


#Main lambda function
def lambda_handler(event, context):
    return createOktaAccount(event)