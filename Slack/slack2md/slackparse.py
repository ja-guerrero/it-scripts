
from mdutils.mdutils import MdUtils
from mdutils import Html
import json
from logging import getLogger
import time
from logger import init_logging
import requests
import os
import re
import boto3
from dotenv import load_dotenv
from botocore.config import Config
import botocore
init_logging()
load_dotenv()

#Set Signature version if encryption is used, must upadte client to contain config=config
config = Config(signature_version='s3v4')

#If not configured, uses default/curent profile in ~/.aws/cofnig
AWS_CLIENT = os.getenv("xxx")
AWS_SECRET = os.getenv("xxx")
AWS_BUCKET = os.getenv("xxx")

#Creates boto3 Client
s3client = boto3.client('s3',aws_access_key_id=AWS_CLIENT, aws_secret_access_key=AWS_SECRET)

#File Excpetion list to avoid Get request for anthing else besides image formats
fileException = ['gdoc','csv','xlsx','docx','dox','ppxt','gsheet']

#Initiate logger
logging= getLogger()

#Class to filter json and upload files
class Slack_Parser:

    def __init__(self, Channel_MetaData: list, file=None) -> None:
        """
        Parameters
        ----------
        Channel_MetaData : list
            json of slack export

        file : string
            Used for call backs and error logs
        """
        self.file = file
        self.Channel_MetaData = Channel_MetaData
        self.filterMessage(self.Channel_MetaData)
        

    def filterMessage(self, Message_Data):
        new_channel_data = []
        for message in Message_Data:
            try:
                NewMessage = Message(message)
                NewMessage.atUserFind(NewMessage.text)
                new_channel_data.append(NewMessage)
            except Exception as e:
                logging.error((f"{self.file}: Message Could not Be Parsed: {e}"))
        self.Channel_MetaData = new_channel_data

    def getData(self):
        return self.Channel_MetaData
    
    def uploadFiletoS3(self,file= None, link = None, Parent = None, metadata:dict = None, Key:str = None):
        if link:
            r = requests.get(link, stream=True)
            if r.status_code == 200:
                s3client.upload_fileobj(Bucket=f"{AWS_BUCKET}", Fileobj=r.raw, Key=f"{Key}")
                
            else:
                logging.error(f"AWS S3 OBJECT UPLOAD RETURNED POST: {r.status_code}")
        else:
            logging.error(f"SLACK LINK COULD NOT BE FOUND IN JSON: {self.file}")

    
    def getFiles(self, s3Parent):
        for msg in self.Channel_MetaData:
            if msg.files:
                user:str = msg.user
                user= user.replace("/", "")
                for img in msg.files:
                    try: 
                        if img["filetype"] not in fileException:
                            try:
                                # Attempt to head the object to check if it exists
                                s3client.head_object(Bucket=AWS_BUCKET, Key=f"{s3Parent}/{str(img['timestamp'])}-{user}-{img['title'][-1]}.{img['filetype']}".replace(" ", ""))
                            except botocore.exceptions.ClientError as e:
                                if e.response['Error']['Code'] == '404':
                                    url = img["url_private"].replace("\/", '/' )
                                    # Object does not exist, so upload it
                                    self.uploadFiletoS3(link=url, Key= f"{s3Parent}/{str(img['timestamp'])}-{user}-{img['title'][-1]}.{img['filetype']}".replace(" ", ""))
                                else:
                                    # Something went wrong
                                    print(f'Error checking S3 object: {e}')
                            
                    except Exception as err:
                            logging.error(f"{self.file}: {err} FILETYPE NOT FOUND")


    def returnFilePath(self, file):
        return file

    
class Message:
    def __init__(self, Message:dict ) -> dict:
   
        self.Message:dict = Message
        self.user = self.Message["user"] 
        self.ts = self.Message['ts']
        self.text = self.Message["text"]
        self.files = self.Message["files"] if "files" in self.Message else None
        self.replies  = self.Message["replies"] if "replies" in self.Message else None
        self.useridMap()
        

    def useridMap(self):
        with open("slack-user-map.json") as file:
            Users = json.load(file)
        for user in Users:
            if user["userid"] == self.user:
                self.user = user["fullname"]

    def atUserFind(self, text:str):
       res = re.findall("(?<=\<@)(.*?)(?=\>)", text)
       for i in res:  
            search = re.search("(?<=\<@)(.*?)(?=\>)", text)
            text = text.replace(text[search.span()[0] - 2  :search.span()[1] +1 ], f"@{self.getUser(text[search.span()[0]:search.span()[1]])}")
            self.text = text
       
    def getUser(self, id):
        with open("slack-user-map.json") as file:
            Users = json.load(file)
            for user in Users:
                if user["userid"] == id:
                    return(user["fullname"])
 
class md_Document:
    def __init__(self, Content, output,s3parent,isfile=True, filename=None,):
        self.isfile = isfile
        self.filename=filename
        self.user = Content
        self.content = Content
        self.output = output
        self.s3Parent = s3parent
        self.mdFile = MdUtils(file_name=self.output, title="") 
        self.addUserPost()

    def getObject(self, Key):
        signed_url=  s3client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': f"{AWS_BUCKET}",
                'Key': Key
            }
        )
        url = f'https://{os.getenv("BUCKET_NAME")}.s3.amazonaws.com/{Key}'
        return url
    def addUserPost(self):
        for message in self.content:
            user: str = message.user
            reply = self.replyCheck(message)
            if reply:
                self.mdFile.new_paragraph(f"\t {message.user}: {message.text} \t {time.strftime('%a, %d %b %Y %I:%M',time.gmtime(float(message.ts)))}\n")
                if message.files:
                    user= user.replace("/", "")
                    for img in message.files:
                        try:
                            result = s3client.list_objects_v2(Bucket=f"{AWS_BUCKET}", Prefix=f"{os.path.basename(self.s3Parent)}/{str(img['timestamp'])}-{user}-{img['title'][-1]}.{img['filetype']}".replace(" ", ""))
                            if 'Contents' in result:

                                path = self.getObject(f"{os.path.basename(self.s3Parent)}/{str(img['timestamp'])}-{user}-{img['title'][-1]}.{img['filetype']}".replace(" ", ""))
                                self.mdFile.new_paragraph(Html.image(path=path))
                        except Exception as e:
                            logging.error(f"{self.filename} AWS S3 URL COULD NOT BE RETRIEVED:{e}")
            else: 
                self.mdFile.new_header(level=2, title=f"{message.user} \t {time.strftime('%a, %d %b %Y %I:%M',time.gmtime(float(message.ts)))}", add_table_of_contents="n")
                self.mdFile.new_line(message.text)
                self.mdFile.write("\n")
                

                if message.files:
                    for img in message.files:
                        try:
                            if img['filetype'] not in ['gdoc','csv','xlsx','docx','dox','ppxt','gsheet']:
                                try:
                                    user= user.replace("/", "")
                                    path = self.getObject(f"{self.s3Parent}/{str(img['timestamp'])}-{user}-{img['title'][-1]}.{img['filetype']}".replace(" ", ""))
                                    self.mdFile.new_paragraph(Html.image(path=path))
                                except Exception as e:
                                    logging.error(f"AWS FILE COULD NOT BE UPLOADED:{self.filename}")
                        except Exception as e:
                            logging.error(f"FILETYPE COULD NOT BE FOUND,{self.filename}")
                

    def replyCheck(self, currmessage):
        thread = currmessage.Message["ts"]
        for msg in self.content:
            user:str = msg.user.replace("/","\\")
            
            if msg.replies:
                for reply in msg.replies:
                    if thread == reply["ts"]:
                        return reply

    def getmdtext(self):
        return self.mdFile.get_md_text()

    def download(self):
        mdContent = self.mdFile.get_md_text()
        if self.isfile:
            with open(self.output+ ".md", "w") as f:
                f.write(mdContent)
                f.close()
        if not self.isfile:
            with open(f"{self.output}/{self.filename}.md", 'w') as f:
                f.write(mdContent)
                f.close()