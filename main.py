"""External ENV file support (API KEY)"""
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

import requests
import json

class apiRequest(object):
    def __init__(self, params, id):
        self.url = os.getenv("TEST_RAIL_BASE_URL")
        self.username = os.getenv("TEST_RAIL_USERNAME")
        self.password = os.getenv("TEST_RAIL_API_KEY") # or password
        self.headers = {
            'Content-type': 'application/json'
            }
        self.planId = "/" + id
        self.params = "/" + params
        self.response = False
        self.payload = False

    def sendRequest(self):
        """Session Example: Use session to send api requests with auth parameters"""
        session = requests.Session()
        session.auth = (self.username, self.password)
        auth = session.post(self.url+self.params)

        print("Sending request",self.url+self.params+"...")
        self.response = session.get(self.url + self.params + self.planId, headers=self.headers, data=self.payload)
        print("Response Status Code:",self.response.status_code)

        # Validate request status
        if self.response.status_code != 200:
            return False
        else:
            self.responseDisplay()
            return self.response

    def responseDisplay(self):
        """Display the response"""
        if self.response == False:
            return False
        print(json.dumps(self.response.json(), indent=4))

# Create request instance for get plan
getPlan = apiRequest("get_plan", "52314")
# Send a get plan request and store the response in getPlan.response
getPlan.sendRequest()
# Display the response all pretty
getPlan.responseDisplay()
