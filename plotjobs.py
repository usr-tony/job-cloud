from sqlconnect import connect_to_db
from exclude import generic_name, recruiters
import boto3
from time import time
import json
import os

s3_bucket_name = 'websitebucket000'

def main():
    database = []
    functions = [by_company, by_industry, by_sector]
    for f in functions:
        data = job_filter(f)
        data['time'] = time()
        database.append(data)

    with open('./components/data.json', 'w') as file:
        file.write(json.dumps(database))
    
    os.system('npm run build')
    with open('dist/index.html', 'rb') as f1:
        upload_to_s3(f1, 'jobs', 'html')

    with open('dist/bundle.js', 'rb') as f2:
        upload_to_s3(f2, 'bundle', 'js')


def job_filter(func):
    con, cur = connect_to_db()
    data, title, filename = func(cur)
    con.close()
    new_filename = filename
    return collect_data(data, title, new_filename)

def by_company(cur):
    raw_data = sql_query(cur, 'company')
    q = [] 
    excluded_companies = generic_name + recruiters # excludes recruitment firms and job aggregator sites.
    for row in raw_data:
        include_row = True
        for company in excluded_companies:
            if company in row[0].lower():
                include_row = False
                break
        
        if include_row:
            q.append(row)
    
    title = 'Current job listings on seek.com.au by company'
    filename = 'By company'
    return q, title, filename

def by_industry(cur):
    raw_data = sql_query(cur, 'industry')
    filename = 'By industry'
    q = []
    for row in raw_data:
        include_row = True
        if row[0] == 'Other': # no industry specified
            include_row = False

        if include_row:
            q.append(row)

    title = 'Current job listings on seek.com.au by industry'
    return q, title, filename

def by_sector(cur):
    q = sql_query(cur, 'sector')
    title = 'Current job listings on seek.com.au by sector'
    filename = 'By sector'
    return q, title, filename

def by_city(cur):
    q = sql_query(cur, 'city')
    title = 'Current job listings on seek.com.au by city'
    filename = 'By city'
    return q, title, filename

def sql_query(cur, param):
    cur.execute(f'SELECT {param}, COUNT(*) AS cnt FROM jobs GROUP BY {param} ORDER BY cnt DESC')
    return cur.fetchall()

def collect_data(data, title, name): # generates a html plot

    data = {
        "name" : name,
        "title" : title,
        "data": data
    }
    return data

def upload_to_s3(obj, filename, tp):
    boto3.resource('s3')\
        .Bucket(s3_bucket_name)\
        .put_object(Key=filename + '.' + tp, Body=obj, ContentType=tp)

if __name__ == '__main__':
    main()
