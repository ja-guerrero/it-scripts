## Summary 
This Program is for IT Use. This tool is used to turn slack exports into readable markdown files for Retention Purposes

## Get Started
To get started make sure, you have an up to date repo

If you dont have this repo cloned please run:
``` bash
git clone https://github.com/jaguerrero/it-general-scripts.git
```

If you have the repo, run to make sure all commits are updated locally:
```bash
git pull origin main
```

After you have the updated repository, next we have to install our packages 
To do this please run this command:
``` bash
pip3 install -r requirements.txt
```

## Run the Command 
The main file in this project is json2md.py file. It has 3 Arguments
```bash
-f: file
-d: directory 
-o: output name
```
If you have a singular json file, you can call the command:
```bash
python3 json2md.py -f file.json -o Hello
```
This will output a file call Hello.md
This program is also capable for Directory Enumeration. If you have a directory of json files you can run 
```
python3 json2md.py -d dirpath -o hello
```
This will create a directory call hello that has markdown files concatenated by Month