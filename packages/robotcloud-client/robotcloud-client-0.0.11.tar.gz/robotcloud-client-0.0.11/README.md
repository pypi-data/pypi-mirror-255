# PYTHON ROBOTCLOUD API CLIENT

Python library to access robotcloud endpoints.

## Installation

```bash
pip install robotcloud-client
```
### Environment variables

The environment where your application is running must define the next environment variables
to be able to interact with robotcloud:
- **ROBOTCLOUD_API_KEY**: Should contain the api key of the robotcloud instance you want to interact.  
- **ROBOTCLOUD_ROOT_URL**: Should contain the base URL which point to the robotcloud instance. 
In a local environment can be something like "http://127.0.0.1:8080/robotcloud/1.2"