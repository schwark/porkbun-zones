import zonefile_parser
import requests
import json
from glob import glob
import sys
import re
 
# read credentials
with open('config.json') as f:
    creds = json.load(f)

files = [sys.argv[1]] if len(sys.argv) > 1 else glob('*.zone')

for file in files:
    domain = re.sub(r'\.zone$', '', file)
    with open(file,"r") as stream:
        # update name servers
        ns = [
            "maceio.ns.porkbun.com",
            "curitiba.ns.porkbun.com",
            "salvador.ns.porkbun.com",
            "fortaleza.ns.porkbun.com"
        ]
        r = requests.post(f'https://porkbun.com/api/json/v3/domain/updateNs/{domain}', json={**creds, "ns": ns})
        result = r.json()
        print(result)
        print(f'{domain} : {result["status"]} {result["id"] if "id" in result else result["message"]}')
        
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

        
        
        