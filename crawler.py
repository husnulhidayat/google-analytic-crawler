'''
  Author: Husnul Hidayat
'''

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import sys

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = '{your_key_dir_loc}'
VIEW_ID = '{view_id_of_google_analytic}'

def initialize_analyticsreporting():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics


def get_report(analytics):
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges':
            [
              {
                  'startDate': '8daysAgo', 'endDate': 'today'
              }
            ],
          'metrics':
            [
               {'expression': 'ga:totalEvents'},
               {'expression': 'ga:uniqueEvents'},
               {'expression': 'ga:eventValue'},
               {'expression': 'ga:avgEventValue'}
            ],
          'dimensions':
            [
                {'name': 'ga:eventCategory'},
                {'name': 'ga:eventAction'},
                {'name': 'ga:eventLabel'}
            ]
        }]
      }
  ).execute()

def print_response(response, SEP=","):
  with open('/var/nfs_share/google_analytic/{}.csv'.format(today),'w') as f:
      for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        metricHeaders = list(map(lambda x: x.get('name'), metricHeaders))
        header = SEP.join(dimensionHeaders) + SEP + SEP.join(metricHeaders)
        #print(header)

        for row in report.get('data', {}).get('rows', []):

          dimensions = row.get('dimensions', [])
          dateRangeValues = row.get('metrics', [])

          output =  SEP.join(dimensions)

          for i, values in enumerate(dateRangeValues):

            for metricHeader, value in zip(metricHeaders, values.get('values')):
                output = output + SEP + value

            f.write(output+'\n')

def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  print_response(response)

if __name__ == '__main__':
  today = sys.argv[1]
  main()
