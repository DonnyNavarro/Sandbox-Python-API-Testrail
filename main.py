"""External ENV file support (API KEY)"""
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

import requests
import json
from datetime import datetime

class apiRequest(object):
    def __init__(self, params, id):
        self.baseUrl = os.getenv("TEST_RAIL_BASE_URL")
        self.username = os.getenv("TEST_RAIL_USERNAME")
        self.password = os.getenv("TEST_RAIL_API_KEY") # or password
        self.params = params
        self.planId = str(id)
        self.headers = {'Content-type': 'application/json'}
        self.payload = False
        self.response = False

    def sendRequest(self):
        """Send the API to Testrail defined in in this instance"""
        session = requests.Session() # create a session request instance
        session.auth = (self.username, self.password) # set auth for the session instance
        requestUrl = self.baseUrl+"/"+self.params+"/"+self.planId

        print("Sending request...")
        print("  ..."+requestUrl)
        self.response = session.get(requestUrl, headers=self.headers, data=self.payload)
        print("  ...Response Status Code:",self.response.status_code)

        # Validate request status
        if self.response.status_code != 200:
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
        


"""Examples"""
# Create request instance for get plan
getPlan = apiRequest("get_plan", "52314")
# Send a get plan request and store the response in getPlan.response
getPlan.sendRequest()
# Display the response all pretty
getPlan.responseDisplay()
getPlan.responseExport()