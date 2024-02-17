from flask import Flask
from vulzap.db.sql import SQL

app = Flask(__name__)

def get_xss_data():
    sql = SQL()
    query = "select cve,payload,is_vuln from xss_report"
    data = sql.select(query, ())
    return data

def get_sqli_data():
    sql = SQL()
    query = "select cve,payload,is_vuln from sqli_report"
    data = sql.select(query, ())
    return data

def get_ssrf_data():
    sql = SQL()
    query = "select cve,payload,is_vuln from ssrf_report"
    data = sql.select(query, ())
    return data

def get_detail_from_db(cve_id):
    sql = SQL()
    tables = ['xss_report', 'sqli_report', 'ssrf_report']
    details = []
    
    for table in tables:
        query = f"SELECT cve,url,param,payload FROM {table} WHERE cve = %s"
        data = sql.select(query, (cve_id,))
        if data:
            for item in data:
                details.append((table, *item))

    return details