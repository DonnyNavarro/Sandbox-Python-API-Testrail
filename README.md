# Sandbox-Python-API-Testrail
 
Exploring Testrail API features and what all we can automate with it

## Design
- Class for apiRequest sets out the basic structure of an apiRequest so that it can be instanced to manage request parameters and response
  - self.sendRequest sends the request of an apiRequest instance
- Payloads are the main complicated item when they are needed, requiring user decisions to choose what payload options to include

## Example: Blackboard Approach
- **Description:** A working example of using a commandline interface to queue up Testrail destinations and deliver results to them within a python script
- **File:** bb_example.py