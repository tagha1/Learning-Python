import fileinput
import os
import json
import moveFile
import subprocess
import re

fullname = input('Please Enter Fullname \n').upper()

# naming the folder
file_name = fullname.lower() + 'pass'

# this will add a new folder inside the new path
new_folder = r'./passes/' + file_name
if not os.path.exists(new_folder):
    os.makedirs(new_folder)
    new_folder.replace(" ","")

# this is copying the file and creating a new file with the cardholders
# name and storing it inside passes directory
cpy_pst = moveFile.cpy_file('./json/pass.json', new_folder)
cpy_pst = moveFile.cpy_file('./json/manifest.json', new_folder)
cpy_pst = moveFile.cpy_file('./img/icon.png', new_folder)
cpy_pst = moveFile.cpy_file('./img/icon@2x.png', new_folder)
cpy_pst = moveFile.cpy_file('./img/logo.png', new_folder)
cpy_pst = moveFile.cpy_file('./img/logo@2x.png', new_folder)
cpy_pst = moveFile.cpy_file('./img/thumbnail.png', new_folder)
cpy_pst = moveFile.cpy_file('./img/thumbnail@2x.png', new_folder)
cpy_pst = moveFile.cpy_file('Certificates.p12', new_folder)
cpy_pst = moveFile.cpy_file('passcertificate.pem', new_folder)
cpy_pst = moveFile.cpy_file('passkey.pem', new_folder)
cpy_pst = moveFile.cpy_file('WWDR.pem', new_folder)

# changing the name inside PassJson
with fileinput.FileInput("./"+new_folder+"/pass.json", inplace=True, backup='') as file:
    for line in file:
        print(line.replace("$$Name$$", fullname), end= ' ')

# this will move to a different directory
os.chdir(new_folder)

# name_sha is grabbing the file and creating the sha1 key
# name_filt is removing everything besides the key
# name_key is the variable for just the sha1 key
strip_sha = subprocess.run(['openssl', 'sha1', 'thumbnail.png'], stdout=subprocess.PIPE)
sk_filt = re.search("b\'SHA1\(thumbnail.png\)= ([0-9a-z]+)", str(strip_sha.stdout))
strip_key = sk_filt.group(1)

strip2x_sha = subprocess.run(['openssl', 'sha1', 'thumbnail@2x.png'], stdout=subprocess.PIPE)
sk2x_filt = re.search("b\'SHA1\(thumbnail@2x.png\)= ([0-9a-z]+)", str(strip2x_sha.stdout))
strip2x_key = sk2x_filt.group(1)

icon_sha = subprocess.run(['openssl', 'sha1', 'icon.png'], stdout=subprocess.PIPE)
ick_filt = re.search("b\'SHA1\(icon.png\)= ([0-9a-z]+)", str(icon_sha.stdout))
icon_key = ick_filt.group(1)

icon2x_sha = subprocess.run(['openssl', 'sha1', 'icon@2x.png'], stdout=subprocess.PIPE)
ick2x_filt = re.search("b\'SHA1\(icon@2x.png\)= ([0-9a-z]+)", str(icon2x_sha.stdout))
icon2x_key = ick2x_filt.group(1)

logo_sha = subprocess.run(['openssl', 'sha1', 'logo.png'], stdout=subprocess.PIPE)
lk_filt = re.search("b\'SHA1\(logo.png\)= ([0-9a-z]+)", str(logo_sha.stdout))
logo_key = lk_filt.group(1)

logo2x_sha = subprocess.run(['openssl', 'sha1', 'logo@2x.png'], stdout=subprocess.PIPE)
lk2x_filt = re.search("b\'SHA1\(logo@2x.png\)= ([0-9a-z]+)", str(logo2x_sha.stdout))
logo2x_key = lk2x_filt.group(1)

pass_sha = subprocess.run(['openssl', 'sha1', 'pass.json'], stdout=subprocess.PIPE)
pass_filt = re.search("b\'SHA1\(pass.json\)= ([0-9a-z]+)", str(pass_sha.stdout))
pass_key = pass_filt.group(1)

# grabbing the sha1 keys and adding them to manifestJson file
fileWrite = open("./manifest.json", 'w')
with fileWrite as f:
    json.dump({
    "thumbnail.png":strip_key,
    "thumbnail@2x.png":strip2x_key,
    "icon.png":icon_key,
    "icon@2x.png":icon2x_key,
    "logo.png":logo_key,
    "logo@2x.png":logo2x_key,
    "pass.json":pass_key
}, f, indent=4)

fileRead = open("./manifest.json", 'r')
text = fileRead.read()
fileRead.close()

#pk passs name
pk_pass = fullname +'.pkpass'

# this will create the signature file
subprocess.call(['openssl', 'smime', '-binary', '-sign', '-certfile', 'WWDR.pem', '-signer', 'passcertificate.pem', '-inkey', 'passkey.pem', '-in', 'manifest.json', '-out', 'signature', '-outform', 'DER', '-passin', 'pass:12345'])

# this will run the shell command to zip up the file
subprocess.call(['zip', '-r', pk_pass, 'manifest.json', 'pass.json', 'signature', 'logo.png', 'logo@2x.png', 'icon.png', 'icon@2x.png', 'thumbnail.png', 'thumbnail@2x.png'])