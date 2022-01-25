import requests
from bs4 import BeautifulSoup
import re
import ast
from time import sleep, time
from random import random
import threading
from sqlconnect import create_sql_db 
import plotjobs
import datetime


def manager():
    while True:
        print('scraping')
        print(datetime.datetime.now())
        main()
        print('removing old jobs')
        print(datetime.datetime.now())
        remove_old_jobs() # by default jobs older than 30 days are deleted
        print('generating html pages')
        print(datetime.datetime.now())
        plotjobs.main()
        print('sleeping for 12 hours')
        print(datetime.datetime.now())
        sleep(60 * 60 * 12)


def main():
    con, cur = create_sql_db()
    starting_job_id = find_largest_job_id(cur)
    if starting_job_id == None or starting_job_id == '':
        inp = input('enter the id (number at the end of seek.com.au/job/[* this number *]) of a preferably older listing to start search on')
        starting_job_id = int(inp)
    else:
        starting_job_id += 1

    consec_errors = 0
    for i in range(999999):
        try:
            output = Page(starting_job_id + i)
            output['details'] = output['details'].encode('unicode_escape')
            output['time'] = str(round(time()))
            cur.execute(
                'INSERT INTO jobs VALUES (' + ','.join(['%s' for i in range(15)]) + ')',
                [output[o] for o in output]
            )
            con.commit()
            print(output['id'], output['title'], output['company'], end='\r')
            consec_errors = 0
        except Exception as e:
            if '404' in str(e) or '410' in str(e):
                pass
            else:
                print('ERROR', starting_job_id + i, e)

            consec_errors += 1

        if consec_errors > 50:
            con.close()
            break
            
        sleep(random()/10)


def remove_old_jobs():
    con, cur = create_sql_db()
    time_threshold = str(round(time()) - (60 * 60 * 24 * 30))
    cur.execute('SELECT id, time FROM jobs')
    data = cur.fetchall()
    for r in data:
        print('id', r[0])
        print('time', r[1])
        if r[1] > time_threshold:
            cur.execute(f'DELETE FROM jobs WHERE id > {r[0]}')
            break

    con.close()


def find_largest_job_id(cur):
    cur.execute('SELECT MAX(id) FROM jobs')
    largest = cur.fetchone()[0] 
    return largest


def Page(job_id):
    header = {
    "Host": "www.seek.com.au",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "TE": "trailers"
    }
    base_url = 'https://www.seek.com.au/job/'
    url = base_url + str(job_id)
    r = requests.get(url, headers=header)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    tag, = soup.select('[data-automation="job-detail-page"]')
    
    # first parse goes through main body of each listing to obtain most of the information, not all especially
    # job location and job industry / sector are hard to parse effectively as id's are not in the tag
    values = {
        'job-detail-title': [], 
        'advertiser-name': [], 
        'jobAdDetails': [], 
        'job-detail-page': [], 
        'job-detail-work-type': []
    }
    for s in tag.strings:
        if re.search('[A-Za-z]', s):
            v = '' + s
            for i in range(50):
                s = s.parent
                val = s.attrs.get('data-automation')
                if val in values and val != None:
                    values[val].append(v.strip())
                    break
    
    # This part attempts to parse the script tag from the end from the end of the html file with the attribute of 
    # data-automation = server-state as it contains easily organised job location, job sector / industry
    tags = soup.body.find_all('script')
    for tag in tags:
        if 'server-state' == tag.attrs.get('data-automation'):
            tt = tag.text
            break
    
    length = len('window.SEEK_REDUX_DATA = ')
    a = tt.index('window.SEEK_REDUX_DATA = ')
    b = tt.index('window.SEEK_APP_CONFIG = ')
    tt = tt[a + length : b].strip()
    a = tt.index('"locationHierarchy":')
    b = tt.index(',"salary"')
    tt = tt[a:b]
    replacements = {
        'true': 'True',
        'false': 'False',
        'nothing': 'None',
        'undefined': 'None',
        'none': 'None',
        'null': 'None'
    }
    for rep in replacements:
        tt = tt.replace(rep, replacements[rep])

    d = ast.literal_eval('{'+ tt +'}')
    # end of second part, d is the dictionary representing the results of this section
    output = {
        'id': job_id,
        'title': values['job-detail-title'][0],
        'company': values['advertiser-name'][0],
        'nation': d['locationHierarchy']['nation'],
        'state': d['locationHierarchy']['state'],
        'city': d['locationHierarchy']['city'],
        'area': d['locationHierarchy']['area'],
        'suburb': d['locationHierarchy']['suburb'],
        'sector_id': d['classification']['id'],
        'sector': d['classification']['description'],
        'industry_id': d['subClassification']['id'],
        'industry': d['subClassification']['description'],
        'work_type': '\n'.join(values['job-detail-work-type']),
        'details': '\n'.join(values['jobAdDetails'])
    }
    
    return output


if __name__ == '__main__':
    manager()
