import requests
import logging
import os
from http.client import HTTPConnection  # py3
import sys
import argparse
from urllib.parse import quote

importtype = "junit"

def urlencode(name):
    return quote(name, safe="")

parser = argparse.ArgumentParser(description='Sync a number of commits before a specific commit')

parser.add_argument('--url', type=str, required=True,
                    help='Enter your organization url')
parser.add_argument('--project', type=str, required=True,
                    help='Enter project name')
parser.add_argument('--apikey', type=str, required=True,
                    help='The API key to communicate with API')
parser.add_argument('--commit', type=str, required=True,
                    help='Enter the commit that would be the starter')
parser.add_argument('--report', type=str, required=True,
                    help='Enter the report.  Currently only supports a single file')
parser.add_argument('--branch', type=str, required=True,
                    help='Enter the explicity branch to process commit')
parser.add_argument('--testsuite', type=str, required=True,
                    help='Enter the testsuite')
parser.add_argument('--importtype', type=str, required=True,
                    help='Enter the import type junit or trx')
parser.add_argument('--repo_name', type=str, required=False, default='',
                    help='Define repository name')


args = parser.parse_args()
url = args.url.rstrip('/')
project = args.project
apikey = args.apikey
commit = args.commit
branch = args.branch
filepath = args.report
repository = args.repo_name
testsuite = args.testsuite
importtype = args.importtype

testsuiteencoded = urlencode(testsuite)
projectencoded = urlencode(project)
testsuiteencoded = testsuite
projectencoded = project

def testimport():

    log = logging.getLogger('urllib3')
    log.setLevel(logging.DEBUG)

    # logging from urllib3 to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    # print statements from `http.client.HTTPConnection` to console/stdout
    HTTPConnection.debuglevel = 1
    print("importing results")
    print(filepath)

    sizeOfFile = os.path.getsize(filepath)

    apiurl = url + "/api/external/import/"

    payload = {
        "type": importtype,
        "commit": commit,
        "project_name": projectencoded,
        "test_suite_name": testsuiteencoded,
        "repo": repository,
        "import_type": "prioritized",
    }

    files = {
        "file": open(filepath, "rb"),
    }

    headers = {
        "token": apikey,
    }

    print(headers)
    print(payload)
    print(apiurl)

    response = requests.post(apiurl, headers=headers, data=payload, files=files)

    print("file import sent")
    if response.status_code >= 500:
        print(
            (
                "[!] [{0}] Server Error {1}".format(
                    response.status_code, response.content.decode("utf-8")
                )
            )
        )
    elif response.status_code == 404:
        print(("[!] [{0}] URL not found: []".format(response.status_code)))
    elif response.status_code == 401:
        print(("[!] [{0}] Authentication Failed".format(response.status_code)))
    elif response.status_code == 400:
        print(("[!] [{0}] Bad Request: Content: {1}".format(response.status_code, response.content)))
    elif response.status_code >= 300:
        print(("[!] [{0}] Unexpected Redirect".format(response.status_code)))
    elif response.status_code == 200 or response.status_code == 201:
        print("success")
    else:
        print(
            (
                "[?] Unexpected Error: [HTTP {0}]: Content: {1}".format(
                    response.status_code, response.content
                )
            )
        )

if __name__ == '__main__':
    testimport()