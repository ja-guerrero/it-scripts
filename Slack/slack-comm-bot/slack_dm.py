import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import csv
import argparse
load_dotenv()

# Set the Slack bot token environment variable
SLACK_API = os.getenv("xx")


# Message to send to users. {} is a placeholder that will be filled in with user's first name
message_template = "Hello {}, this is a test message. This app was created by @gentianhyseni to test an efficient way to mass DM employees on Slack"

# Define a list of user IDs to send the message to, you can find this from a Slack user Export.

# Initialize a Slack API client
client = WebClient(token=SLACK_API)

# Iterate over the list of user IDs


def getSlackID(email):
    #Get Slack ID from email using Client
    response = client.users_lookupByEmail(email=email)
    #Get UserID from response
    return(response['user']['id'])

# Function to read csv data and turn it into an arrady of dictionaries: Array[Dict]
def read_csv(filename):
    #Define empty array
    data = []
    #Open csv file and read it into an array of dictionaries
    with open(filename, newline='') as csvfile:
        #Read csv file into dictionaries
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return(data)

def send_message(user_id, message):
    """Sends a message to a user on Slack."""
    try:
        response = client.users_info(user=user_id)
        user = response["user"]
        first_name = user["real_name"].split()[0]
        personalized_message = message.format(first_name)
        client.chat_postMessage(channel=user_id, text=personalized_message)
        print(f"Message sent to {user['real_name']} ({user_id})")
    except SlackApiError as e:
        print(f"Error sending message to {user_id}: {e}")


def main(csvfile= None):
    user_ids = []
    data = read_csv(csvfile)
    for user in data:
        try:
            slackID = getSlackID(user['user.email'])
            user_ids.append(slackID)
        except SlackApiError as e:
            print(f"Error Getting slackID for {user['user.email']}: {e}")
    for user_id in user_ids:
        try:
            send_message(user_id, message_template)
        except SlackApiError as e:
            print(f"Error Sending Slack Message for {user_id}: {e}")
    

if __name__ == '__main__':
    #Create argument parser
    args = argparse.ArgumentParser()
    #Add arguments
    args.add_argument('-f', '--file', help='CSV file with user data', required=True)
    #Parse arguments
    args = args.parse_args()
    #Run main function
    main(args.file)

