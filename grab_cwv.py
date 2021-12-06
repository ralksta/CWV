"""
grab_cwv.py: Running Audits with CRUX API to get domain performance insights

Input Format is a CSV file with one origin / row
Output Format is a CSV file with core web vital stats for that origin

"""

import csv
import sys
import time
import json
import re
from datetime import date
import os.path
import requests
import constants

#HEADER
headers = {
    'Content-Type': 'application/json',
}
#APIKEY
params = (
    ('key',constants.crux_api_key),
)

class Audit:

    """ An Audit object runs the CWV Checks.

    Typical usage example:

    MyAudit = Audit()
    MyAudit.open_input_csv(input)
    MyAudit.prep_url(URL)
    MyAudit.get_domain_audit()

    """

    def __init__(self):
        self.dataset = None
        self.api_origin_str = None
        self.domain_input= None
        self.output_csv_name = "cwvchecks.csv"
        self.domain_list = []

        #if output csv not exist yet, write csv header once
        if not os.path.isfile(self.output_csv_name):
            self.write_output_csv_header()


    def prep_url(self,domain_input):

        """Checks input domain for redirects & prepares string for apicall.  """
        self.domain_input = domain_input

        #if domain doesn't end with trailing slash, add one
        if not re.findall(r'\/$',self.domain_input):
            self.domain_input = self.domain_input + "/"

        print("***", self.domain_input, "-> checking for redirects ***")

        #send request to domain to check for redirects
        try:
            responses = requests.get(self.domain_input, timeout=50)
            #IF response url is different - overwrite input url
            if responses.url != self.domain_input:
                print("***",self.domain_input, "-> redirected to",responses.url,"***")
                self.domain_input = responses.url

        except Exception:
            print("*** Checking for redirects failed -> continuing with input URL ***")

        #build string for crux api
        self.api_origin_str = '{"origin": "'+self.domain_input+'"}'
        self.dataset = [self.domain_input,self.api_origin_str]

    def show(self):
        """ Prints CRUX Api String for debugging. """
        print("dataset:",self.dataset)

    #get JSON from API and prepare output
    def get_domain_audit(self):
        """Calls CRUX API and prepares cwv insights for output."""


        print("***", self.domain_input,"-> collecting Core Web Vitals Data ***")
        response = requests.post('https://chromeuxreport.googleapis.com/v1/records:queryRecord'
                                , headers=headers, params=params, data=self.dataset[1])

        if response.ok:
            j_data = json.loads(response.content)

            #save to export json file - could be done more efficiently with a loop I guess
            with open('exportOOP.json', 'w', encoding='utf-8') as json_file:
                json.dump(j_data, json_file, ensure_ascii=False, indent=4)

                final_url = j_data['record']['key']['origin']
                lcp_raw = j_data['record']['metrics']['largest_contentful_paint']
                fid_raw = j_data['record']['metrics']['first_input_delay']
                cls_raw = j_data['record']['metrics']['first_input_delay']

            lcp = {
                  "p75": lcp_raw['percentiles']['p75'],
                  "threshold": lcp_raw['histogram'][0]['end'],
                  "value": round(lcp_raw['histogram'][0]['density']*100)
                  }

            fid = {
                  "p75": fid_raw['percentiles']['p75'],
                  "threshold": fid_raw['histogram'][0]['end'],
                  "value": round(fid_raw['histogram'][0]['density']*100)
                  }

            cls= {
                  "p75": float(cls_raw['percentiles']['p75']),
                  "threshold": float(cls_raw['histogram'][0]['end']),
                  "value": round(cls_raw['histogram'][0]['density']*100)
                  }

            #Did the results pass the CWV Threshold?
            cwv_passed = "failed"

            if (lcp["p75"] <= lcp["threshold"] and fid["p75"] <= fid["threshold"]
            and cls["p75"] <= cls["threshold"]):
                cwv_passed = "passed"

            #Output to CSV
            with open(self.output_csv_name, 'a', encoding='utf-8') as csv_output_file:
                writer = csv.writer(csv_output_file,delimiter =';')
                cwv_text = [final_url
                            ,cwv_passed
                            ,date.today()
                            ,lcp["p75"]
                            ,lcp["value"]
                            ,fid["p75"]
                            ,fid["value"]
                            ,cls["p75"]
                            ,cls["value"]]

                writer.writerow(cwv_text)
                print("***", final_url,"-> writing Core Web Vitals to csv ***\n")

    def write_output_csv_header(self):
        """ Writes CSV Header for inital file creation  """

        #Output to CSV
        with open(self.output_csv_name, 'a', encoding='utf-8') as csv_output_file:
            writer = csv.writer(csv_output_file,delimiter =';')
            cwv_header = ['Origin'
                        ,'Core Web Vitals passed'
                        ,'Date'
                        ,'LCP75P in ms'
                        ,'LCP good in %'
                        ,'FID75P in ms'
                        ,'FID good in %'
                        ,'CLS75P'
                        ,'CLS good in %']

            writer.writerow(cwv_header)

    def open_input_csv(self,input_csv):
        """ open CSV from commandline."""

        csv_file = input_csv[1]

        #Read Rows for Domains
        with open(csv_file,'r', encoding='utf-8') as csv_file:
            csv_reader_object = csv.reader(csv_file, delimiter=';')
            for row in csv_reader_object:
                self.domain_list.append(row[0])

MyAudit = Audit()
MyAudit.open_input_csv(sys.argv) #Input via sys input

#For Each Domain in List run Audit
if len(MyAudit.domain_list) > 0:
    for i in MyAudit.domain_list:
        MyAudit.prep_url(i)
        MyAudit.get_domain_audit()
        time.sleep(0.5)
    print("|||||| Core Web Vitals written to:", MyAudit.output_csv_name, "||||||")
