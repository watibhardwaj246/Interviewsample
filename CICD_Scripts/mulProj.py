#-----------------------------------------------------------
#-----------------------------------------------------------
#-------------@Author: nishant.kumar_3@philips.com----------
#-----------------------------------------------------------
#-----------------------------------------------------------

from XLParser import xl
from CI_lib_v3 import revision
import time

obj1 = xl()
count, lis = obj1.xl_Parse()

#print("Count: ",count)
print(lis)
global val
val = 0
#while val != count:
while True:
    for l in range(0, count):
        #print ("Inside")
        #print(lis[l])
        val = val+1
        appName = lis[l][0]
        env = lis[l][1]
        user = lis[l][2]
        apiKey = lis[l][3]
        ut_pwd = lis[l][4]
        jk_tkn = lis[l][5]
        br_name = lis[l][6]
        utest = lis[l][7]
        func_aut = lis[l][8]
        branch = lis[l][9]
        print("********************Placeholder for Multiple projects******************************")
        obj = revision(appName, user, apiKey, env, ut_pwd, jk_tkn, br_name, utest, func_aut, branch)
        build_required, latest_rev = obj.revision_api()
        if build_required:
            print("    Proceeding with next steps...")
            #Creating a new build
            packageID = obj.api_call(latest_rev)
            #print("************----------***********",packageID)
            stat = obj.pkg_list(packageID)
            if stat:
                #trigger Environment stop API
                stopEnv_Res = obj.stop_EnvApi()
                if stopEnv_Res == 200:
                    print("    Build Sucessfull :",packageID)
                    print ("    Validating status of environments...")
                    env_stat = obj.env_StatusApi()
                    if env_stat == "Stopped":
                        print("    Environment Stopped!!!")
                        #Validating Response for Transport Build
                        res_tb = obj.transport_build(packageID)
                        """Need to wait for some time- approx 1 mins 10 secs for Package ID to get build"""
                        while res_tb !=200:
                            print("    Waiting for Package Build...")
                            print("===========================================")
                            time.sleep(5)
                            print ("    Check if time sleep 30 sec is required?")
                            print("===========================================")
                            res_tb = obj.transport_build(packageID)
                        if res_tb == 200:
                            print("    Transport Build Sucessful, proceeding to next steps...")
                            print("    Starting Environment...")
                            envFlag = obj.start_EnvApi()
                            if envFlag:
                                """Placeholder for Triggering Unit Tests"""
                                if utest == "Y":
                                    print("    Unit Testing Module")
                                    res_UTTrigger = obj.trigger_UT()
                                    print("    Response for Triggering Unit Tests: ",res_UTTrigger)
                                    if res_UTTrigger == 204:
                                        time.sleep(5)
                                        print ("    Fetching Unit Test Results...")
                                        res_UTRes, res_UT = obj.ut_Results()
                                        print("    Unit Test Results: \n",res_UT)
                                else:
                                    print("    Proceeding to Trigger Functional Suite...")
                                    obj.triggerFT()
                                    print("    Functional Execution Completed.....!!!!")
                        else:
                            print("    Check details for Transport build response Error code: ",str(res_tb))
                else:
                    print("    Unable to Stop the Environment, trying again...")
        else:
            print("    Moving to next Projects....")
            #print(type(count))
            time.sleep(5)
    
