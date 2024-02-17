import requests

from vulzap.db.models import SqliReport
from vulzap.db.models import Endpoint

SQLI_PAYLOADS = [
    "%27",  # '
    "%22",  # ""
]

SQLI_BLACKLIST = ["id", "select", "id", "report", "search", "cat"]


class Scan:
    def __init__(
        self,
        level=1,
        Cookie=None,
    ):
        self._level = level
        self._payload = SQLI_PAYLOADS
        self._patterns = SQLI_BLACKLIST

        self.res = requests.Session()
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

        if Cookie != None:
            self.res.headers.update({'User-Agent': user_agent})
            self.res.headers.update({'Cookie': Cookie})     

    def has_common_element(self, arr1, arr2):
        for element in arr1:
            if element in arr2:
                return True
        return False


    def find_suspicious_param(self, data):

        for key, params in data.items():            
            if self.has_common_element(params["GET"] + params["POST"], self._patterns) == False:
                del data[key]

        return data

    def create_request_params(self, parameters_set, value):
        request_params = {}

        for param in parameters_set:
            request_params[param] = value

        return request_params

    def sqli_is_vulnerable(self, response):
        if str(response.status_code)[0] == "5":
            return True

        errors = {
            # MySQL
            "you have an error in your sql syntax;",
            "warning: mysql",
            # SQL Server
            "unclosed quotation mark after the character string",
            # Oracle
            "quoted string not properly terminated",
        }
        for error in errors:
            # if you find one of these errors, return True
            if error in response.content.decode().lower():
                return True
        # no error detected
        return False

    def attack(self, suspicious_param):
        result_data = []

        for payload in self._payload:
            for url, methods in suspicious_param.items():

                for method, params in methods.items():
                    # URL에 대해 GET 또는 POST 요청을 보낼 때 사용되는 코드
                    if method == "GET":
                        query_params = "&".join(
                            f"{param}={payload}" for param in params
                        )
                        full_url = f"{url}?{query_params}"
                        response = self.res.get(full_url)
                    elif method == "POST":
                        # POST 요청을 보내기 위한 코드
                        data_payload = {param: payload for param in params}
                        response = self.res.post(url, data=data_payload)

                    if self.sqli_is_vulnerable(response):
                        result_data.append(
                            {
                                "url": url,
                                "payload": payload,
                                "param": methods["GET"],
                                "data": methods["POST"],
                            }
                        )
                        print(
                            f"[+] SQLI 취약점이 의심되는 부분을 발견했습니다. 메소드: {method}, 링크: {response.url}, GET 파라미터: {params}, 삽입 페이로드: {payload}"
                        )

        return result_data
    
    def crawl_data_extract(self):
        data = {}
        crawl_data = Endpoint.value()

        for i in range(len(crawl_data)):
            if crawl_data[i][2] == "": continue

            if crawl_data[i][0] not in data:
                data[crawl_data[i][0]] = {"GET":[], "POST":[]}

            if crawl_data[i][1] == "GET":
                data[crawl_data[i][0]]["GET"].append(crawl_data[i][2])

            if crawl_data[i][1] == "POST":
                data[crawl_data[i][0]]["POST"].append(crawl_data[i][2])

        return data

    def crawl_data_scan(self):
        crawl_data = self.crawl_data_extract()
        self.run(crawl_data)

    def return_value(self, suspicious_param):
        result = []
        
        for key, params in suspicious_param.items():
            result.extend(params['GET'])
            result.extend(params['POST'])
        
        result = set(result)
        result = list(result)

        return result

    def run(self, data):
        suspicious_param = self.find_suspicious_param(data)

        if len(suspicious_param) != 0:
            print(f"[+] 의심되는 SQLI 파라미터를 발견했습니다 :", self.return_value(suspicious_param))
        else:
            print("[-] 의심되는 SQLI 파라미터를 발견하지 못했습니다.")
            return

        # sqli_report = SqliReport(url=url, match=True)

        # db에 발견한 의심되는 데이터 넣기
        # TODO: 사용하는지 안하는지 기억이 안나서 일단 DB에 안 넣었어요 :(
        if self._level == 1:            
            for key, params in suspicious_param.items():
                sqli_report = SqliReport(
                        url=key,
                        is_vuln=False,
                        payload=None,
                        param=params["GET"],
                        data=params["POST"],
                    )
                sqli_report.save()

        # db에 공격 수행한 결과, 성공 여부 넣기
        if self._level == 2:
            results = self.attack(suspicious_param)

            for result in results:
                sqli_report = SqliReport(
                    url=result["url"],
                    is_vuln=True,
                    payload=result["payload"],
                    param=result["param"],
                    data=result["data"],
                )
                sqli_report.save()


if __name__ == "__main__":
    # sqli_scan = Scan()
    # sqli_scan.crawl_data_scan()

    example_data = {
        "http://testasp.vulnweb.com/test.asp": {
            "GET": ["cat"],
            "POST": [],
        },
        "http://testasp.vulnweb.com/showforum.asp": {
            "GET": ["id"],
            "POST": [],
        },
        "http://ec2-13-209-98-240.ap-northeast-2.compute.amazonaws.com/DVWA/vulnerabilities/sqli/": {
            "GET": ["id"],
            "POST": [],
        }
    }

    sqli_scan = Scan(level=1, Cookie="security=low; PHPSESSID=squbt2sfoep0r0dutab2p0ljnq")
    result = sqli_scan.run(example_data)
