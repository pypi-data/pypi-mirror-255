import os

from flask import Flask, jsonify, render_template, request

from vulzap.core.crawl import Crawl
from vulzap.db.models import SqliReport, XssReport
from vulzap.settings import Env
from vulzap.database import app, get_sqli_data, get_ssrf_data, get_xss_data, get_detail_from_db

pwd = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=f"{pwd}/templates",
    static_folder=f"{pwd}/static",
)


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        url = request.form["url"]
        target = request.form.get("targetInput")
        header = request.form.get("headerInput", "{}")
        output = request.form.get("outputInput")

    return render_template("index.html", error=error)


@app.route("/output", methods=["GET"])
def output():
    return render_template("output.html")

@app.route("/get_table_data", methods=["GET"])
def get_table_data():
    table_name = request.args.get("table")

    if table_name == "xss_report":
        data = get_xss_data()
    elif table_name == "sqli_report":
        data = get_sqli_data()
    elif table_name == "ssrf_report":
        data = get_ssrf_data()
    else:
        return jsonify(success=False, message="Invalid table name"), 400

    return jsonify(
        success=True,
        data=[dict(zip(["cve", "payload", "is_vuln"], item)) for item in data],
    )

@app.route("/get_cve_detail", methods=["GET"])
def get_cve_detail():
    cve_id = request.args.get("cve")
    
    detail = get_detail_from_db(cve_id) 
    if detail:
        return jsonify(
            success=True,
            data=[dict(zip(["table", "cve", "url", "param", "payload"], item)) for item in detail],
        )
    else:
        return jsonify(success=False, message="No details found for this CVE"), 400

@app.route('/save_db_info', methods=['POST'])
def save_db_info():
    data = request.form
    host = data.get('host')
    port = data.get('port')
    name = data.get('name')
    user = data.get('user')
    password = data.get('password')

    print(host, port, name, user, password)
    env = Env()
    setattr(env, 'DB_HOST', host)
    setattr(env, 'DB_PORT', port)
    setattr(env, 'DB_NAME', name)
    setattr(env, 'DB_USER', user)
    setattr(env, 'DB_PASSWD', password)
    env.save()

    return jsonify(success=True)

@app.route('/interaction', methods=["GET"])
def interaction():
    return render_template('interaction.html')

@app.route("/run_crawl", methods=["POST"])
def run_crawl():
    url = request.form["url"]
    target = request.form.get("targetInput")
    header = request.form.get("headerInput")
    output = request.form.get("outputInput")

    # TODO: depth 및 headless 옵션 추가
    # crawl = Crawl(depth=0, headless=True)
    crawl = Crawl()
    crawl_result = crawl.run(
        base=url,
        header=header,
    )

    xss_checked = request.form.get("xss")
    sqli_checked = request.form.get("sqlInjection")
    ssrf_checked = request.form.get("ssrf")

    xss_data = get_xss_data() if xss_checked else None
    sqli_data = get_sqli_data() if sqli_checked else None
    ssrf_data = get_ssrf_data() if ssrf_checked else None

    if xss_checked:
        xss_exploit_result = xss_exploit_main()  # xss_exploit_main 함수 실행
        print("XSS Exploits Executed:", xss_exploit_result)

    if sqli_checked:
        sqli_exploit_result = sqli_exploit_main()  # sqli_exploit_main 함수 실행
        print("SQL Injection Exploits Executed:", sqli_exploit_result)
        
    return jsonify(success=True, xss=xss_data, sqli=sqli_data, ssrf=ssrf_data)
