import requests 
import time
import datetime
import sys
from requests.auth import HTTPBasicAuth
import json
from bs4 import BeautifulSoup
from OpenSSL import crypto, SSL

#The PW Informations you have to fill out manually
PW = ['enter your username here','enter your password here','enter your profile number here']
#with this parameter you can set the inverval in that should be refreshed
refresh_minutes = 15 #at the moment max 59 minutes!
#to minimize the server communication to the necessary minimum, a night pause is added. The 2 parameters
#specify in which time interval of the day should be refresed
#as an example [6,22] means that only between 6:00 and 21:59 the routes are reloaded 
refresh_houer_time_frame = [6,22]

#this is the login url to that the login data is send
url = 'https://dashboard.hammerhead.io/v1/auth/token'

#this is the time the last time was logged in
start_time = datetime.datetime.now()
#set the last logged in time to one hour ago, to beeing sure a new login is done
start_time = start_time - datetime.timedelta(hours = 1)
#set the default time frame for the auth token to 3600sec. This will later be set to the real expire time frame
expire_time_seconds = 3600

#copied default headers from browser to look not to suspicies
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
	'Host': 'dashboard.hammerhead.io',
    'Origin': 'https://dashboard.hammerhead.io',
    'Referer': 'https://dashboard.hammerhead.io/auth/signin',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

#function for creating an ssl cert for the https communication. This will be once created on start-up and is valid 10 years
def cert_gen(
    emailAddress="emailAddress",
    commonName="commonName",
    countryName="NT",
    localityName="localityName",
    stateOrProvinceName="stateOrProvinceName",
    organizationName="organizationName",
    organizationUnitName="organizationUnitName",
    serialNumber=0,
    validityStartInSeconds=0,
    validityEndInSeconds=10*365*24*60*60,
    KEY_FILE = "private.key",
    CERT_FILE="selfsigned.crt"):
    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(CERT_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))

#this creates the payload for the login with the login data and specifies the login type via password
login_data = {
    'grant_type': 'password',
    'username': PW[0],
    'password': PW[1]    
 }

print('Creating Cert')
cert_gen()
print('Cert created') 
while True:
    nowhour = datetime.datetime.now().hour
    if nowhour > (refresh_houer_time_frame[0] - 1) and nowhour < refresh_houer_time_frame[1]:
        with requests.Session() as s:
            timedifference = datetime.datetime.now() - start_time
            if timedifference.seconds < (expire_time_seconds - (refresh_minutes * 60)):
                print('enough rest time '+str(60 - (timedifference.seconds / 60))+' minutes')
            else:
                print('logging in')
                r = s.post(url, headers=headers, data=login_data, verify=True,  cert =('./selfsigned.crt','./private.key'),auth=HTTPBasicAuth(PW[0], PW[1]))
                if r.status_code != 200:
                    print('Error during login. Maybe Password or Username wrong')
                    print('waiting for 30 minutes before retry')
                    time.sleep(60 * 30)
                    continue
                start_time = datetime.datetime.now()
                data_json = json.loads(r.content)
                print(data_json)
                headers['Authorization'] = 'Bearer ' + data_json['access_token']
                expire_time_seconds = int(data_json['expires_in'])
                print('logged in, refresh list')
            r = s.post('https://dashboard.hammerhead.io/v1/users/'+PW[2]+'/routes/sync', headers=headers, verify=True,  cert =('./selfsigned.crt','./private.key'))
            if r.status_code != 200:
                print('Error during refresh. Maybe User ID wrong')
                print('waiting for 30 minutes before retry')
                time.sleep(60 * 30)
                continue
            print(r.content)
    else:
        print('outside of refresh time frame')
    time.sleep(60*refresh_minutes)
