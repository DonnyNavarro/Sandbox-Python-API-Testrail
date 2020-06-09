"""External ENV file support (API KEY)"""
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

import requests
import json

class apiRequest(object):
    def __init__(self, params):
        self.url = os.getenv("TEST_RAIL_BASE_URL")
        self.username = os.getenv("TEST_RAIL_USERNAME")
        self.password = os.getenv("TEST_RAIL_API_KEY") # or password
        self.headers = {
            'Content-type': 'application/json'
            }
        self.planId = "/52314"
        self.params = params

    # def requestPlan(self, testrunId=None):
    #     """Get Test Plan details for the Testplan of the testrunId"""
    #     if not testrunId:
    #         testrunId = self.testrunId
    #     params = "/get_plan/"
    #     data = self.sendRequest(params+testrunId)
    #     return data

    def sendRequest(self):
        """Session Example: Use session to send api requests with auth parameters"""
        session = requests.Session()
        session.auth = (self.username, self.password)
        auth = session.post(self.url+self.params)

        print("Sending request",self.url+self.params+"...")
        response = session.get(self.url + self.params + self.planId, headers=self.headers)
        print("Response Status Code:",response.status_code)

        # Validate request status
        if response.status_code != 200:
            displayJson(response)
            return False
        else:
            return response

def displayJson(jsonData):
    """Print a JSON all pretty like"""
    jsonDict = jsonData.json()
    print(json.dumps(jsonDict, indent=4))
    # end basic session


getPlan = apiRequest("/get_plan")
planDetail = getPlan.sendRequest()
displayJson(planDetail) if planDetail else False
