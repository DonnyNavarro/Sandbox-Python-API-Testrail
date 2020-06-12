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
    def __init__(self, requestType, urlParams, payload={}, files={}):
        """Create an api request instance. 
        
        requestType is str "get", "post" etc. 
        urlParams is the tail of the url
        payload is a dict that will be sent as a json
        files is a dict reference to a locale file"""
        self.baseUrl = os.getenv("TEST_RAIL_BASE_URL")
        self.username = os.getenv("TEST_RAIL_USERNAME")
        self.password = os.getenv("TEST_RAIL_API_KEY") # or password
        self.requestType = requestType
        self.urlParams = urlParams
        self.headers = {'Content-type': 'application/json'}
        self.payload = payload
        self.files = files
        self.response = False

        if files: #Change content type when attaching files
            self.headers = {'Content-type': 'multipart/form-data'}

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
            json=self.payload,
            files=self.files
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
        print("  ...Response Reason:",self.response.reason)
        print(json.dumps(self.response.json(), indent=4))

    def responseExport(self):
        """Export the response as a JSON to a local folder"""
        if not self.checkResponse():
            return False
        time = datetime.today().strftime('%Y-%m-%d-%H%M%S')
        # Save the log file
        with open("logs/"+time+".json", "w") as outfile:
            json.dump(self.response.json(), outfile, indent=4)

def nowTime():
    return datetime.today().strftime('%Y-%m-%d-%H%M%S')

def promptYesno(message):
    """Prompt the user with the message and only accept yes/no as input. Return true if they say yes."""
    choice = ""
    while not choice:
        choice = input(message+" [y/n] ")
        if choice.lower() in ["yes", "y", "yep", "yup", "sure"]:
            return True
        elif choice.lower() in ["no", "n", "nope", "nah"]:
            return False
        else:
            print("ERROR: Input not recognized. Choose yes or no\n")
            choice = ""

def promptNum(message):
    """Prompt the user with the message and only accept numbers as input. Return the input."""
    choice = 0
    while not choice:
        choice = input(message+" [number] ")
        try:
            int(choice)
        except:
            print("ERROR: Input not recognized. Choose a number\n")
            choice = 0
    return choice

def promptText(message):
    """Prompt the user with the message and only accept text as input. Return the input."""
    choice = ""
    while not choice:
        choice = input(message+" [text] ")
        try:
            str(choice)
        except:
            print("ERROR: Input not recognized. Choose text\n")
            choice = ""
    return choice
    
if __name__ == '__main__':
    projectNum = 0
    suiteNum = 0
    milestoneNum = 0
    milestoneName = ""
    milestoneResponse = False
    testsList = {}

    testrunReuse = promptYesno("Would you like to use a previous Testrun?")
    if testrunReuse:
        # Reuse a Testrun ID!
        testrunNum = promptNum("Testrun ID #")
        testrunResponse = apiRequest("get", "/get_run/"+testrunNum)
        testrunResponse.sendRequest()
        # testrunResponse.responseDisplay()
        projectNum = testrunResponse.response.json()["project_id"] #jic
        milestoneNum = testrunResponse.response.json()["milestone_id"] #jic
        suiteNum = testrunResponse.response.json()["suite_id"] #jic
    else:
        # Creating a new Testrun! But first check if we want Milestones!
        milestone = promptYesno("Would you like to use a Milestone at all?")
        if milestone:
            # Use a Milestone!
            milestoneReuse = promptYesno("Would you like to use a previous Milestone?")
            if milestoneReuse:
                # Reuse a Milestone ID!
                milestoneNum = promptNum("Milestone ID #")
                milestoneResponse = apiRequest("get", "/get_milestone/"+milestoneNum)
                milestoneResponse.sendRequest()
                # milestoneResponse.responseDisplay()
                milestoneResponse.name = milestoneResponse.response.json()["name"]
                print("Milestone:",milestoneResponse.name)
                milestoneResponse.id = milestoneResponse.response.json()["id"]
                projectNum = milestoneResponse.response.json()["project_id"] #jic
            else:
                # Create a new Milestone!
                projectNum = promptNum("What is the Testrail Project Number?") # this should usually be replaced by an environmental
                milestoneName = promptText("What would you like to name the new Milestone?")
                milestoneResponse = apiRequest("post", "/add_milestone/"+str(projectNum), {"name": milestoneName})
                milestoneResponse.sendRequest()
                # milestoneResponse.responseDisplay()
                milestoneResponse.id = milestoneResponse.response.json()["id"]
                milestoneNum = milestoneResponse.response.json()["id"]

        # Create a new Testrun!
        testrunName = promptText("What would you like to name the new Testrun?")
        suiteNum = promptNum("Test Suite ID #") if not suiteNum else suiteNum
        projectNum = promptNum("Testrail Project #") if not projectNum else projectNum
        testrunPayload = {
            "suite_id": suiteNum,
            "name": testrunName
        }
        if milestone:
            testrunPayload["milestone_id"] = milestoneNum
        testrunResponse = apiRequest("post", "/add_run/"+str(projectNum), testrunPayload)
        testrunResponse.sendRequest()
        # testrunResponse.responseDisplay()
        testrunResponse.id = testrunResponse.response.json()["id"]
        testrunNum = testrunResponse.response.json()["id"]
        projectNum = testrunResponse.response.json()["project_id"] # jic
        milestoneNum = testrunResponse.response.json()["milestone_id"] #jic
        suiteNum = testrunResponse.response.json()["suite_id"] #jic

    # Now that we have our Testrun defined
    # Get test IDs and store them in testsList dict
    testsResponse = apiRequest("get", "/get_tests/"+str(testrunNum))
    testsResponse.sendRequest()
    # testsResponse.responseDisplay()
    for test in testsResponse.response.json():
        # Organize tests by title so specific ones can have their ids referenced
        testsList[test["title"]] = {
            "id": test["id"],
            "case_id": test["case_id"]
        }
    """ FINAL RESULT: testsList dict of test IDs to send results to """
    # At this point we should have a set of results previously prepared that we want to send
    # Results to report will need a test name to correspond to the TC name in Testrail
    # By matching the name we can get the testsList[name]["id"] in order to send results there
    print(json.dumps(testsList, indent=4))

def reportResult(testname, testsList, status, comment):
    """Report a result for testname to Testrail, based on ID mapping in the testsList
    
    testname: Should match the name of the testcase in testrail
    testsList: a dict of testnames to testrail id numbers
    result: pass/fail/etc
    comment: Whatever you want printed in the testrail report
    """
    # Testrail status codes mapped to human readable
    statusMap = {
        "pass": 1,
        "passed": 1,
        "blocked": 2,
        "untested": 3,
        "retest": 4,
        "fail": 5
    }
    payload = {
        "status_id": statusMap[status],
        "comment": comment
    }
    addResult = apiRequest("post", "/add_result/"+str(testsList[testname]["id"]), payload)
    addResult.sendRequest()

