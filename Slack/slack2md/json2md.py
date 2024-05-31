import argparse
from slackparse import *
import json
from logging import getLogger
from logger import init_logging

logger = getLogger()
def organizeData(dir):
    data = {}
    for (dirpath, dirnames, filenames) in os.walk(dir):
        for filename in filenames:
            if not filename.startswith('.'):
                file = os.sep.join([dirpath, filename])
                year = filename.split("-")[0]
                month = filename.split("-")[1]
                if year in data:
                    if month in data[year]:
                        data[year][month].append(file)
                    else: 
                        data[year][month] = [file]
                else:
                    data[year] = {month: [file]}
    return data

def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-f", "--file", help="Directory of the file you wish to parse")
    argParser.add_argument("-o", "--output", help="Directory of where the Markdown should be downloaded and named")
    argParser.add_argument("-i", "--image",help=" Only Download the Images in the export", action='store_true')
    argParser.add_argument("-d", "--dir",help="Get Markdown of all files in a diredtory")
    args = argParser.parse_args()


    if args.file:
        with open(args.file) as file:
            Channel_data = json.load(file)
        Parse = Slack_Parser(Channel_data)
        
        if args.image:
                Parse.getFiles(args.output)

        else:
            Parse.getFiles(s3Parent="Test")
            document = md_Document(Parse.Channel_MetaData, output=args.output, isfile=True, s3parent="Test")
            document.download()

    if args.dir:
        if args.output:
            os.mkdir(str(args.output))
            output = args.output
        else:
            os.mkdir(str(args.dir))
            output = args.dir
        files = organizeData(args.dir)

        for year in files.keys():
            for month in files[year]:
                with open(f"{output}/{year}-{month}.md","w+") as ym:
                    for day in sorted(files[year][month]):
                        with open(day) as f:
                            Channel_data = json.load(f)
                            f.close()
                        Parse = Slack_Parser(Channel_data, file=day) 
                        Parse.getFiles(s3Parent=os.path.basename(args.dir))
                        document = md_Document(Parse.Channel_MetaData, output=f"{output}",s3parent=os.path.basename(args.dir) ,isfile=False, filename=day)
                        ym.write(document.getmdtext())
                    ym.close()

                #files.append(filename)
                
                #directories.append(file)
        
        
            #filename = file.split("/")[-1]
            #year = int(filename.split("-")[0])
            #month = int(filename.split("-")[1])
            
            

    #with open(file) as file:
    #    Channel_data = json.load(file)
    #Parse = Slack_Parser(Channel_data, file=filename)
    #if Parse.getFiles():
    #    document = md_Document(Parse.Channel_MetaData, output=f"{output}", isfile=False, filename=filename)
    #    document.download()
        
                
       

main()
