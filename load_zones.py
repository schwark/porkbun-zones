import zonefile_parser
import requests
import json
from glob import glob
 
# read credentials
with open('config.json') as f:
    creds = json.load(f)

files = glob('*.zone')

for file in files:
    domain = file.replace('.zone','')
    with open(file,"r") as stream:
        content = stream.read()
        records = zonefile_parser.parse(content)
        
        r = requests.post(f'https://porkbun.com/api/json/v3/dns/retrieve/{domain}', json={**creds})
        result = r.json()
        print(result)

        for record in records:
            insert = {
                "type": record.rtype
            }
            name = record.name.replace(f'.{domain}.','').replace(f'{domain}.','')
            if name: insert["name"] = name 
            if record.ttl: insert["ttl"] = record.ttl 
            if "MX" == record.rtype:
                insert['content'] = record.rdata['host']
                insert['prio'] = record.rdata['priority']
            else:
                content = '\"'+record.rdata["value"]+'\"' if (' ' in record.rdata['value']) else record.rdata['value']
                insert['content'] = content
            r = requests.post(f'https://porkbun.com/api/json/v3/dns/create/{domain}', json={**insert, **creds})
            result = r.json()
            print(f'{insert["type"]} {insert["content"]} : {result["status"]} {result["id"] if "id" in result else result["message"]}')

        
        
        