# devops-restapi
Devops Assignment - RESTful API and Agile development

[![Build Status](https://travis-ci.org/rachitmehrotra1/devops-restapi.svg?branch=master)](https://travis-ci.org/rachitmehrotra1/devops-restapi)
[![codecov](https://codecov.io/gh/rachitmehrotra1/devops-restapi/branch/master/graph/badge.svg)](https://codecov.io/gh/rachitmehrotra1/devops-restapi)

This project contains a minimalistic service that lets people (“users”) input in their available times. And then use the “meet” function to find common time that set of users are available to get a meeting time.

Entry points :
/user – to add,remove,update,view user details
/times – to store the available for a user
/meet -  to get a common available time for a set of users

# Running
Runs on localhost:5000 by default

You can user bluemix by setting the VCAP_SERVICES environment variable 

Uses redis on localhost:6379 by default
```
$ python server.py
```

# Documentation

Visit the api root for all information about endpoints and possibilities:

http://localhost:5000/

Swagger UI Documentation and Test Endpoints are avaialable on Bluemix Address 

http://devchronops.mybluemix.net/

