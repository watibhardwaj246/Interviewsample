#-----------------------------------------------------------
#-----------------------------------------------------------
#-----------------------------------------------------------
#-----------------------------------------------------------

#required libraries
import httplib2
import urllib
import json
import time
import sqlite3
#Library for validating file existance
import os.path
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class revision():
    def __init__(self,appName, user, apiKey, env, ut_pwd, jk_tkn, br_name, utest, func_aut, branch):
        self.appName = appName
        self.user = user
        self.apiKey = apiKey
        self.env = env
        self.utPWD = str(ut_pwd)
        self.jk_token = jk_tkn
        self.branchName = br_name
        self.utst = utest
        self.fAut = func_aut
        self.branch = branch
    
    def revision_api(self):
        http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.104.34', 9480))
        http.follow_all_redirects = True
        urlh = "https://deploy.mendix.com/api/1/apps/"+self.appName+"/branches/"+self.branchName+"/revisions"
        headers = {"mendix-apikey" : self.apiKey,"mendix-username": self.user,'Content-type': 'application/json'}
        response, content = http.request(urlh, 'GET', headers=headers, body='')
        out = content.decode("utf-8")
        print("-------------------------------------------------")
        data = json.loads(out)
        #Fetch last and latest revisions
        last_rev = data[-1].get('Number')
        latest_rev = data[0].get('Number')
        """Check for existance of database"""
        environment = self.env.lower()
        build_required = False
        if environment != "production":
            db_name = self.appName+"-"+environment+"-"+self.branch
            print("Database Name: ", db_name)
            if os.path.isfile(db_name+".db"):
                print("Database Status: Database exists")
                """Create a database connection to a SQLite database to retrieve last version"""
                conn = sqlite3.connect(db_name+".db")
                """Creating Cursor"""
                cur = conn.cursor()
                """Fetch value of Last version from Table"""
                cur.execute ("SELECT currver from appver")
                cv = cur.fetchone()[0]
                print ("    Lastest Version: ", cv)
                conn.close()
                if cv == latest_rev:
                    print("    No New build available!!!")
                else:
                    #empty list to hold revision histories >= last revision history
                    rev_list = []
                    for item in data:
                        rev = item.get('Number')
                        #print ("--------------------------",rev)
                        if rev > cv:
                            rev_list.append(item)
                            #print(rev_list)
                            #saving data onto Json file-----> Optional
                            with open('rev_v1.json', 'w') as f:
                                json.dump(rev_list, f, ensure_ascii=False)
                            #update database with polled values
                            updated_lastRev, updated_latestRev = self.update_db (cv, latest_rev)
                            print ("    Updated Last revision in DB: ", updated_lastRev)
                            print ("    Updated Latest revision in DB: ", updated_latestRev)
                            build_required = True
            else:
                print("Database not present, Creating one!!!")
                """ create a database connection to a SQLite database """
                conn = sqlite3.connect(db_name+".db")
                #print(sqlite3.version)
                conn.execute ('''CREATE TABLE appver
                                 (appid TEXT NOT NULL,
                                 lastver INT NOT NULL,
                                 currver INT NOT NULL);''')
                

                """Creating Cursor"""
                c = conn.cursor()
                #row = [(db_name,1,1)]
                c.execute ('INSERT INTO appver (appid, lastver, currver) VALUES (:appid,:lastver,:currver)',(db_name,last_rev,latest_rev))
                conn.commit()
                """Fetch value of Last version from Table"""
                c.execute ("SELECT lastver from appver")
                lv = c.fetchone()[0]
                print ("    Last Version: ", lv)
                """Fetch value of Lastest version from Table"""
                c.execute ("SELECT currver from appver")
                cv = c.fetchone()[0]
                print ("    Latest Version: ", cv)
                conn.close()
                with open('rev_v1.json', 'w') as f:
                    json.dump(data, f, ensure_ascii=False)
                build_required = True
        else:
            db_name = self.appName
            print("This section needs to be Developed for Production environment if in case of Need...")
        return build_required, latest_rev
    
    def api_call(self, latest_rev):
        try:
            http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.104.34', 9480))
            #http.follow_all_redirects are specifically used for POST requests if there is a proxy set in mid
            http.follow_all_redirects = True
            header = {'mendix-apikey' : self.apiKey, 'mendix-username':self.user,'Content-type': 'application/json', 'postman-token': 'a88d61ab-da16-b979-720e-14292fc0b214', 'cache-control': 'no-cache'}
            url = "https://deploy.mendix.com/api/1/apps/"+self.appName+"/packages"
            bod = {"Branch" : self.branchName, "Revision" : latest_rev, "Version" : "1.0.0", "Description" : "Continuous Integration-Test Build"}
            #body = urllib2.urlencode(bod)
            #headers = headerss
            #response, content = http.request(url , method , headers= {'mendix-apikey' : 'ae4299f2-8b97-4012-bbfb-b039664d57e9', 'mendix-username':'viral.patel@philips.com','Content-type': 'application/json', 'postman-token': 'a88d61ab-da16-b979-720e-14292fc0b214', 'cache-control': 'no-cache'}, body= json.dumps(bod))
            response, content = http.request(url ,'POST' , headers= header, body= json.dumps(bod))
            out1 = content.decode("utf-8")
            #print(out1)
            #print(out1)
            data = json.loads(out1)
            pkgID = data["PackageId"]
            #print(response.status)
        except Exception as e:
            print(e)
        return pkgID
    def pkg_list(self, pk_id):
        try:
            http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.104.34', 9480))
            http.follow_all_redirects = True
            header = {'mendix-apikey' : self.apiKey, 'mendix-username':self.user,'Accept': '*/*'}
            url = "https://deploy.mendix.com/api/1/apps/"+self.appName+"/packages"
            response, content = http.request(url ,'GET' , headers= header, body= '')
            out1 = content.decode("utf-8")
            #print(out1)
            #print(out1)
            data = json.loads(out1)
            print("------------------------------")
            for p_id in data:
                if p_id["PackageId"] == pk_id:
                    print(p_id["PackageId"])
                    #print(p_id["CreationDate"])
                    #print(p_id["Status"])
                    #print(p_id["Status"] == "Building")
                    if (p_id["Status"] == "Building"):
                        print ("    Package Status: ", p_id["Status"])
                        print ("    Please Wait, your package is currently Building...")
                        time.sleep(10)
                        self.pkg_list(pk_id)
                    elif (p_id["Status"] == "Succeeded"):
                        print ("    Package Status: ", p_id["Status"])
                        print("    Package Build Succeeded...")
        except Exception as e:
            print(e)
        return True

    def stop_EnvApi(self):
        try:
            http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.104.34', 9480))
            http.follow_all_redirects = True
            url = "https://deploy.mendix.com/api/1/apps/"+self.appName+"/environments/"+self.env+"/stop"
            header = {'mendix-apikey' : self.apiKey, 'mendix-username':self.user}
            response, content = http.request(url , 'POST' , headers= header, body= '')
            out1 = content.decode("utf-8")
            #print(response)
        except Exception as e:
            print(e)
        return response.status
    def start_EnvApi(self):
        try:
            http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.104.34', 9480))
            http.follow_all_redirects = True
            url = "https://deploy.mendix.com/api/1/apps/"+self.appName+"/environments/"+self.env+"/start"
            header = {'Accept' : '*/*','mendix-apikey' : self.apiKey, 'mendix-username':self.user, 'Content-Type':'application/json'}
            bod = {"AutoSyncDb" : 'true'}
            response, content = http.request(url , 'POST' , headers= header, body= json.dumps(bod))
            out1 = content.decode("utf-8")
            #print(response.status)
            env_st = False
            if response.status ==200:
                """Triggered Environment start API, now wait till environment status is Running as part of env_StatusApi"""
                while self.env_StatusApi()!="Running":
                    print("    Waiting for Environment to get fully running...")
                    time.sleep(30)
                env_st = True
            elif response.status == 500:
                print("    Environment is already up & Running")
                pass
            else:
                print("    This Section needs to be updated-- Start_EnvApi")
            #print(out1)
        except Exception as e:
            print(e)
        return env_st
    def env_StatusApi(self):
        try:
            http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.104.34', 9480))
            http.follow_all_redirects = True
            url = "https://deploy.mendix.com/api/1/apps/"+self.appName+"/environments/"
            header = {'mendix-apikey' : self.apiKey, 'mendix-username':self.user}
            response, content = http.request(url , 'GET' , headers= header, body= '')
            out1 = content.decode("utf-8")
            env_data = json.loads(out1)
            #print(type(env_data))
            for entry in env_data:
                #print(entry["Mode"])
                if entry["Mode"].lower()==self.env.lower():
                    print(entry["Status"])
                    env_stat = entry["Status"]
                    print("-------------------")
                else:
                    pass
        except Exception as e:
            print(e)
        return env_stat
    def db_exists(self, last_rev):
        print("I am @ db_exists Function")
        #Converting value of env variable to lower case
        environment = self.env.lower()
        db_flag = False
        if environment != "production":
            db_name = self.appName+"-"+environment+"-"+self.branch
            print(db_name)
            if os.path.isfile(db_name+".db"):
                print("Database exists")
                """Create a database connection to a SQLite database to retrieve last version"""
                conn = sqlite3.connect(db_name+".db")
                """Creating Cursor"""
                cur = conn.cursor()
                """Fetch value of Last version from Table"""
                cur.execute ("SELECT lastver from appver")
                lv = cur.fetchone()[0]
                print ("Last Version: ", lv)
                conn.close()
                db_flag = True
            else:
                print("Database not present, Creating one!!!")
                """ create a database connection to a SQLite database """
                conn = sqlite3.connect(db_name+".db")
                print(sqlite3.version)
                conn.execute ('''CREATE TABLE appver
                                 (appid TEXT NOT NULL,
                                 lastver INT NOT NULL,
                                 currver INT NOT NULL);''')
                

                """Creating Cursor"""
                c = conn.cursor()
                #row = [(db_name,1,1)]
                c.execute ('INSERT INTO appver (appid, lastver, currver) VALUES (:appid,:lastver,:currver)',(db_name,last_rev,last_rev))
                conn.commit()
                """Fetch value of Last version from Table"""
                c.execute ("SELECT lastver from appver")
                lv = c.fetchone()[0]
                print ("    Last Version: ", lv)
                conn.close()
                db_flag = True
        else:
            db_name = self.appName+"-"+environment+"-"+self.branch
            print("This section needs to be Developed for Production environment if in case of Need...")
            db_flag = False
        return db_flag, lv
    def update_db(self, lastVer, latestVer):
        print("I am @ update_db Function- This function is used to update the last & latest version fields to Latest version")
        #print (latestVer)
        #Converting value of env variable to lower case
        environment = self.env.lower()
        db_name = self.appName+"-"+environment+"-"+self.branch
        """Create a database connection to a SQLite database to retrieve last version"""
        conn = sqlite3.connect(db_name+".db")
        """Creating Cursor"""
        cur = conn.cursor()
        """Updating db value of Latest version in Table-- This section needs to be updated from Insert statement to """
        cur.execute ("UPDATE appver SET appid=?,lastver=?, currver=?",(db_name,lastVer,latestVer))
        conn.commit()
        #This section is for Testing
        #print ("New updated values for Last Version & Latest Version: ")
        cur.execute ("SELECT lastver from appver")
        lastV = cur.fetchone()[0]
        print ("    Last Version: ", lastV)
        """Testing for Latest Version"""
        cur.execute ("SELECT currver from appver")
        latestV = cur.fetchone()[0]
        print ("    Latest Version: ", latestV)
        conn.close()
        return lastV, latestV
    def transport_build(self, packID):
        try:
            """This API call take abount 2 mins to respond"""
            #print(packID)
            http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.104.34', 9480))
            http.follow_all_redirects = True
            environment = self.env.lower()
            if environment == 'accp':
                url = "https://deploy.mendix.com/api/1/apps/"+self.appName+"/environments/"+environment+"/transport"
            else:
                url = "https://deploy.mendix.com/api/1/apps/"+self.appName+"/environments/"+self.env+"/transport"
            header = {'mendix-apikey' : self.apiKey, 'mendix-username':self.user, 'Content-Type':'application/json'}
            bod = {"PackageId": packID}
            response, content = http.request(url , 'POST' , headers= header, body= json.dumps(bod))
            #res = content.decode("utf-8")
            #print(res)
            print(response.status)
        except Exception as e:
            print(e)
        return response.status
    def trigger_UT(self):
        try:
            """This API is for Triggering Unit Tests"""
            #http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.106.34', 9480))
            http = httplib2.Http()
            http.follow_all_redirects = True
            environment = self.env.lower()
            name = self.appName+"-"+environment
            #print(name)
            url = "https://"+name+".mendixcloud.com/unittests/start"
            header = {'Content-Type':'application/json'}
            bod = {"password": self.utPWD}
            response, content = http.request(url , 'POST' , headers= header, body= json.dumps(bod))
            print("    Unit test Response status: ",response.status)
        except Exception as e:
            print(e)
        return response.status
    def ut_Results(self):
        try:
            """This API is for Collecting Unit Test Results"""
            #http = httplib2.Http(proxy_info=httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, '165.225.106.34', 9480))
            http = httplib2.Http()
            http.follow_all_redirects = True
            environment = self.env.lower()
            name = self.appName+"-"+environment
            url = "https://"+name+".mendixcloud.com/unittests/status"
            #header = ''
            #print ("Password: ",self.utPWD)
            bod = {"password": self.utPWD}
            response, content = http.request(url , 'POST', body= json.dumps(bod))
            res = content.decode("utf-8")
            js = json.loads(res)
            #print(response.status)
            #print (type(res))
            with open('UT_RES_'+name+'.json', 'w') as f:
                json.dump(js, f, ensure_ascii=False)
        except Exception as e:
            print(e)
        return response.status, res
    def triggerFT(self):
        """This Section is for Triggering Functional Test Suite through Jenkins API"""
        driver = webdriver.Firefox(executable_path = "geckodriver.exe")
        proj = self.appName+"-"+self.env+"-"+self.branch
        #driver.get("http://127.0.0.1:9090/job/"+proj+"/build?token="+self.jk_token)
        driver.get("http://127.0.0.1:9090/job/ietportal-test/build?token="+self.jk_token)
        #element = driver.find_element_by_xpath(".//*[@id='j_username']")
        #driver.execute_script("arguments[0].sendkeys('admin');", element)
        time.sleep(5)
        driver.find_element_by_xpath(".//*[@id='main-panel']/div/form/table/tbody/tr[1]/td[2]").send_keys("admin")
        time.sleep(2)
        driver.find_element_by_xpath(".//*[@name = 'j_password']").send_keys("admin")
        time.sleep(2)
        driver.find_element_by_xpath(".//*[@id='yui-gen1-button']").click()
        driver.close()
        driver.quit()
