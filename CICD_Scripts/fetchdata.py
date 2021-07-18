#-----------------------------------------------------------
#-----------------------------------------------------------
#-------------@Author: nishant.kumar_3@philips.com----------
#-----------------------------------------------------------
#-----------------------------------------------------------

#required libraries
import requests
import xml.etree.ElementTree as ET
import json
import time
import openpyxl
import codecs
import re
import base64


class sp_Data():
    def getSharePointData(self):
        wb = openpyxl.load_workbook('ExpectedResults.xlsx')
        sheet = wb.get_sheet_by_name('Sheet1')
        i=2

        #url="https://tst.bluecast.philips.com/ws/WS_SPConnector"
        url="https://acc.inside.iethub.philips.com/ws/WS_SPConnector"
        #headers = {'content-type': 'application/soap+xml'}
        headers = {'content-type': 'text/xml'}
        body = """<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:exam='http://www.example.com/'>
           <soapenv:Header>
              <exam:authentication>
                 <username>wsuser</username>
                 <password>Test123</password>
              </exam:authentication>
           </soapenv:Header>
           <soapenv:Body>
              <exam:DSL_GetSharepointItems>
                 <Where><![CDATA[<And>
                                <Geq><FieldRef Name=\'Modified\' /><Value IncludeTimeValue=\'False\' Type=\'DateTime\'>2018-07-31</Value></Geq>
                    <Leq><FieldRef Name=\'PublishingStartDate\' /><Value IncludeTimeValue=\'True\' Type=\'DateTime\'><Today /></Value></Leq>
                </And>
                <And><Eq><FieldRef Name=\'_ModerationStatus\' /><Value Type=\'Integer\'>0</Value></Eq></And>
                <And><Eq><FieldRef Name=\'RobotsNoIndex\' /><Value Type=\'Integer\'>0</Value></Eq></And>]]></Where>
                 <FieldRef><![CDATA[<FieldRef Name=\'FileLeafRef\' /> 
                <FieldRef Name=\'Title\' />
                <FieldRef Name=\'PhilipsSocialCastId\' />
                <FieldRef Name=\'PhilipsIntranetTags\' />
                <FieldRef Name=\'PhilipsLocation\' />
                <FieldRef Name=\'PublishingPageLayout\' />
                <FieldRef Name=\'ArticleStartDate\' />
                <FieldRef Name=\'TaxKeyword\' />
                <FieldRef Name=\'PhilipsNewsPublisher\' />
                <FieldRef Name=\'PublishingPageContent\' />
                <FieldRef Name=\'PublishingRollupImage\' />
                <FieldRef Name=\'PublishingPageImage\' />
                <FieldRef Name=\'PhiPushNotification\' />
                <FieldRef Name=\'RedirectURL\' />
                <FieldRef Name=\'PublishingStartDate\' />]]></FieldRef>
                 <OrderBy><![CDATA[<FieldRef Name=\'PublishingStartDate\' Ascending=\'False\' />]]></OrderBy>
              </exam:DSL_GetSharepointItems>
           </soapenv:Body>
        </soapenv:Envelope>"""
        #Below Proxy settings are optional
        '''
        proxies = {
          'http': 'http://emea.zscaler.philips.com:9480',
          'https': 'https://emea.zscaler.philips.com:9480',
        }
        '''
        #response = requests.post(url,data=body,headers=headers, proxies = proxies)
        response = requests.post(url,data=body,headers=headers)
        #print(response.text)

        with open('sharepointitems.xml','w') as f:
            f.write(response.text)

        tree = ET.parse('sharepointitems.xml')
        #print(response.text)
        root = ET.fromstring(response.text)
        for data in root.iter('Result'):
            continue
            #print(type(data.text))
        res = data.text
        outres = json.loads(res, strict=False)
        with open('sharepointitems.json','w') as j:
            json.dump(outres, j)
        time.sleep(5)
        with open('sharepointitems.json') as data_file:
            data = json.load(data_file)
        #print("----------------------Launching----------------------------")
        tags=''
        topics = ''
        #Below logic is for extracting current profile topics subscription
        #-----------------------------------------------------------------
        with open('Topics.txt') as f:
            data = f.read()
        regex = ("\\|")
        regexp_new = (",")
        lis = re.split(regex,data)
        #-----------------------------------------------------------------
        for eachtitle in outres['d']['results']:
            #print(str(eachtitle['Title'].encode("iso-8859-15","replace")))
            #Updating excel Sheet with sharepoint data
            sheet['A'+str(i)].value = i-1
            sheet['B'+str(i)].value = str(eachtitle['PublishingPageLayout']['Description'])
            sheet['C'+str(i)].value = str(eachtitle['Title'])
            sheet['D'+str(i)].value = str(eachtitle['PublishingStartDate'])
            sheet['E'+str(i)].value = str(eachtitle['ArticleStartDate'])
            sheet['G'+str(i)].value = str(eachtitle['ID'])
            sheet['H'+str(i)].value = str(eachtitle['Modified'])
            sheet['I'+str(i)].value = str(eachtitle['PublishingPageContent'])
            sheet['L'+str(i)].value = str(eachtitle['PhiPushNotification'])
            #print("-----------------------")
            try:
                flag = True
                for trial in eachtitle['PhilipsIntranetTags']['results']:
                    if flag:
                        #print("Under IF Condition")
                        topics = trial['Label']
                        flag = False
                    else:
                        #print("Under Else Condition")
                        topics = topics + "," + trial['Label']
                #sheet['F'+str(i)].value = str(topics)
            except UnboundLocalError:
                print("Under Exception Block...")
                continue
            try:
                loc_flag =True
                for loc in eachtitle['PhilipsLocation']['results']:
                    if loc_flag:
                        #print("Under IF Condition")
                        location = topics+','+loc['Label']
                        loc_flag = False
                    else:
                        #print("Under Else Condition")
                        location = topics+","+location + "," + loc['Label']
                sheet['F'+str(i)].value = str(location)
                #Getting list of comma seperated items as seperate items of list
                lis_new = re.split(regexp_new, location)
                for eachitem in lis_new:
                    for ele in lis:
                        if eachitem==ele:
                            sheet['K'+str(i)].value = "Y"
                        else:
                            continue
            except UnboundLocalError:
                print("Under Exception Block...")
                continue
            try:
                tag_flag =True
                for tag in eachtitle['TaxKeyword']['results']:
                    if tag_flag:
                        #print("Under IF Condition")
                        tags = tag['Label']
                        tag_flag = False
                    else:
                        #print("Under Else Condition")
                        tags = tags + "," + tag['Label']
                sheet['J'+str(i)].value = str(tags)
            except UnboundLocalError:
                print("Under Exception Block...")
                continue
            i=i+1
            wb.save("ExpectedResults.xlsx")
    def getProfileData(self):
        #url="https://tst.bluecast.philips.com/ws/WS_SPConnector"
        url = "https://acc.inside.iethub.philips.com/ws/WS_SPConnector"
        #headers = {'content-type': 'application/soap+xml'}
        headers = {'content-type': 'text/xml'}
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:exam="http://www.example.com/">
           <soapenv:Header>
              <exam:authentication>
                 <username>wsuser</username>
                 <password>Test123</password>
              </exam:authentication>
           </soapenv:Header>
           <soapenv:Body>
              <exam:DSL_GetSharepointProfile>
                 <Email>nishant.kumar_3@philips.com</Email>
              </exam:DSL_GetSharepointProfile>
           </soapenv:Body>
        </soapenv:Envelope>"""
        #Below Proxy settings are optional
        proxies = {
          'http': 'http://42.99.164.34:9480',
          'https': 'https://42.99.164.34:9480',
        }
        lis= []
        response = requests.post(url,data=body,headers=headers, proxies = proxies)
        #response = requests.post(url,data=body,headers=headers)
        #with open('profile.xml','w') as f:
            #f.write(response.text)
        #tree = ET.parse('profile.xml')
        root = ET.fromstring(response.text)
        for data in root.iter('Result'):
            continue
            #print(type(data.text))
        res = data.text
        js = json.loads(res)
        with open('profile.json','w') as j:
            json.dump(js, j, ensure_ascii=True)
        time.sleep(5)
        with open('profile.json') as data_file:
            data = json.load(data_file)
        for eachtitle in data['d']['UserProfileProperties']['results']:
            if (eachtitle['Key']=="phIntranetTags"):
                #print(eachtitle['Value'].encode('UTF-8'))
                str1 = eachtitle['Value']
                #print("-----------------------------------------------")
            elif (eachtitle['Key']=="phLocations"):
                #print(eachtitle['Value'].encode('UTF-8'))
                str2 = eachtitle['Value']
        #print("========================================================")
        str3 = str1+"|"+str2
        #print(str3.encode('UTF-8'))
        fil = codecs.open('Topics.txt','w','UTF-8')
        fil.write(str3)
        fil.close()
