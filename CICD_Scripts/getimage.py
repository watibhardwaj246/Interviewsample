import base64
import requests
import xml.etree.ElementTree as ET

url = "https://acc.inside.iethub.philips.com/ws/WS_SPConnector"
#headers = {'content-type': 'application/soap+xml'}
headers = {'content-type': 'text/xml'}
image_id = 13411
body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:exam="http://www.example.com/">
   <soapenv:Header>
      <exam:authentication>
         <username>wsuser</username>
         <password>Test123</password>
      </exam:authentication>
   </soapenv:Header>
   <soapenv:Body>
      <exam:DSL_GetSharepointImage>
         <ID>"""+str(image_id)+"""</ID>
         <ListGUID>da39e43d-c570-4c6d-a865-5f8693d6c99a</ListGUID>
         <ImageType>Thumbnail</ImageType>
         <!--Optional:-->
      </exam:DSL_GetSharepointImage>
   </soapenv:Body>
</soapenv:Envelope>"""
#Below Proxy settings are optional
'''
proxies = {
  'http': 'http://42.99.164.34:9480',
  'https': 'http://42.99.164.34:9480',
}
'''
#lis= []
response = requests.post(url,data=body,headers=headers, )
print(response.text)
tree = ET.parse('sharepointitems.xml')
root = ET.fromstring(response.text)
for data in root.iter('Contents'):
    continue
#print(root)
#print(data)
res = data.text

print("----------Creating an image----------")
#Converting Base64 string to image
#image_64_decode = base64.decodestring(res)
image_64_decode = base64.standard_b64decode(res)
image_result = open('img.jpg', 'wb')
image_result.write(image_64_decode)

