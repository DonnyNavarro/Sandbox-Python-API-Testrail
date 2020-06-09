"""External ENV file support (API KEY)"""
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

import requests
import json
from datetime import datetime
import time

class apiRequest(object):
    def __init__(self, requestType, urlParams, payload={}):
        self.baseUrl = os.getenv("TEST_RAIL_BASE_URL")
        self.username = os.getenv("TEST_RAIL_USERNAME")
        self.password = os.getenv("TEST_RAIL_API_KEY") # or password
        self.requestType = requestType
        self.urlParams = urlParams
        self.headers = {'Content-type': 'application/json'}
        self.payload = payload
        self.response = False

    def sendRequest(self):
        """Send the API to Testrail defined in in this instance"""
        session = requests.Session() # create a session request instance
        session.auth = (self.username, self.password) # set auth for the session instance

        print("Sending request...")
        print("  ..."+self.baseUrl+self.urlParams)
        self.response = session.request(
            self.requestType,
            self.baseUrl+self.urlParams, 
            headers=self.headers, 
            json=self.payload
            )
        print("  ...Response Status Code:",self.response.status_code)

        # Validate request status
        if self.response.status_code != 200:
            self.responseDisplay() # If an error occurs, display it to the user immediately
            return False
        else:
            # Return the response for truth, but its been stored in self.response so it can be called anywhere without catching this return
            return self.response

    def checkResponse(self):
        """Check the current instance for a response. To be used by internal methods that are going to act on self.response."""
        if self.response == False:
            print("There is no response yet. Run self.sendRequest() first.")
            return False
        else:
            return True

    def responseDisplay(self):
        """Display the response"""
        if not self.checkResponse():
            return False
        print(json.dumps(self.response.json(), indent=4))

    def responseExport(self):
        """Export the response as a JSON to a local folder"""
        if not self.checkResponse():
            return False
        time = datetime.today().strftime('-%Y-%m-%d-%H%M%S')
        # Save the log file
        with open("logs/"+self.params+"-response"+time+".json", "w") as outfile:
            json.dump(self.response.json(), outfile, indent=4)
        
def do_getPlan(planId):
    """Example: Get Test Plan Details"""
    # Create request instance for get plan
    getPlan = apiRequest("get", "/get_plan/"+str(planId))
    # Send a get plan request and store the response in getPlan.response
    getPlan.sendRequest()
    # getPlan.responseDisplay() # Display the response all pretty
    # getPlan.responseExport() # Save response to logs folder
    # print(getPlan.response.json()["name"]) # Call a single item from the response
    return getPlan

def do_getPlans(projectId, milestone=""):
    """Example: Get Test Plans from Project"""
    flag = "&created_by=" # return only test plans created by a particular user id
    flag = "&milestone_id="+milestone # return only test plans associated with a particular milestone number
    flag = "&is_completed=0" # return only completed 1 or not completed 0 test plans
    getPlans = apiRequest("get", "/get_plans/"+str(projectId)+flag) 
    getPlans.sendRequest()
    # getPlans.responseDisplay()
    # getPlans.responseExport()

    # # Print all the Plan names in the Project
    # for plan in getPlans.response.json():
    #     print(plan["name"])
    return getPlans

def do_getUser(email):
    """Get user stats from Testrail"""
    myUser = apiRequest("get", "/get_user_by_email&email="+email)
    myUser.sendRequest()
    myUser.userId = myUser.response.json()["id"]
    myUser.name = myUser.response.json()["name"]
    myUser.email = myUser.response.json()["email"]
    print("User:",myUser.userId,myUser.name,myUser.email)
    return myUser

def do_getUsers():
    """Get stats for all the users on this Testrail (Why would we ever need this, creeper)"""
    allUsers = apiRequest("get", "/get_users")
    allUsers.sendRequest()
    # allUsers.responseDisplay()
    return allUsers

def do_addPlan(testName, projectId):
    """Add a new Test Plan to a Project"""
    # Additional capabilities available: Add to Milestone, Add with entries (Testruns)
    payload = {
        "name": testName
        }
    newPlan = apiRequest("post", "/add_plan/"+projectId, payload)
    newPlan.sendRequest()
    newPlan.responseDisplay()
    return NewPlan

def do_updatePlan(planId):
    """Edit a Testplan"""
    # Can edit... name, milestone, assignment...
    payload = {
        "name": "Test Plan with an edited name",
    }
    updatePlan = apiRequest("post", "/update_plan/"+planId, payload)
    updatePlan.sendRequest()
    # updatePlan.responseDisplay()

def do_addPlanEntry(planId, suiteId, testcases=False):
    """Add a Testrun to planId Testplan. Testcases can be specified as an [id list] otherwise all cases in the testsuite will be included.

    Note that Tescase IDs do not include the first letter, just the numbers"""
    # include_all defaults to True, but can be toggled off to use a specific selection of testcases from the testsuite
    payload = {}
    payload["suite_id"] = str(suiteId)

    if testcases:
        payload["include_all"] = False
        payload["case_ids"] = testcases

    newEntry = apiRequest("post", "/add_plan_entry/"+planId, payload)
    newEntry.sendRequest()
    newEntry.responseDisplay()

def do_getStatus():
    """Get all the statuses available for this Testrail. Reveals custom statuses, and their ID values"""
    getStatuses = apiRequest("get", "/get_statuses/")
    getStatuses.sendRequest()
    # getStatuses.responseDisplay()

def do_getRun(runId):
    """Get the details of a particular runID Testrun"""
    check = apiRequest("get", "/get_run/"+runId)
    check.sendRequest()
    # check.responseDisplay()

def do_addResult(testId, result, report="", defects=""):
    """Add a result (pass/fail/etc) to a testId's testcase instance. Report should be included as a string."""
    # Note that it may be tricky finding good programmatic ways to identify testId's. These are not really intended to be entered by the user manually, that would never be efficient

    # Map human statuses to api values. 
    #   Note that Testrail does support custom statuses, 
    #   and a GET request to /get_statuses/ can fetch those custom values
    statusMap = {
        "pass": 1,
        "passed": 1,
        "blocked": 2,
        "untested": 3,
        "retest": 4,
        "fail": 5
    }
    
    # PAYLOAD
    payload = {}
    payload["status_id"] = statusMap[(result).lower()]
    # COMMENT: If report provided was a dict, our output will be ugly for now, but still works
    #   Type: Ultimately this needs to be a string. Markdown will need to be baked into the string before it is sent
    if type(report) == dict:
        report = json.dumps(report)
    payload["comment"] = report
    # DEFECTS: It seems unlikely you have a defect ticket ready when sending automated status report, but if useful it is available
    #   Type: Should be a comma separated string if sending multiple defect links
    payload["defects"] = defects
    # end PAYLOAD

    newResult = apiRequest("post", "/add_result/"+testId, payload)
    newResult.sendRequest()
    # newResult.responseDisplay()
    return newResult


"""Other features available in the API"""
# update_plan_entry Edit a testrun within a testplan
# close_plan


"""Regress"""
# do_getPlan("52314")
# do_getPlans("76")
# do_getUser("donny@ultratesting.us")
# do_getUsers()
# do_addPlan("New Test Plan", "76")
# do_updatePlan("68270")
# do_addPlanEntry("68270", "1474", ["1127199", "1127200"])
# do_getStatus()
# do_getRun("68280")
do_addResult("84420526", "Fail", "A big ole flop")