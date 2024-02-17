import argparse
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from vulzap.db.models import XssReport

XSS_PAYLOADS = [
    '<script>alert("1")</script>',
    '<script>alert("xss")</script>',
    '" onmouseover="alert(1)"',
    "javascript:alert(1)",
]

CVE_DATABASE = {
    "KVE-2023-5153": {
        "payload": "<script>alert(2023-5153)</script>",
        "param": "skin",
        "affected_versions": ["5.5.8.3.1"],
        "target_url": "/shop/listtype.php",
    },
    "VVE-2023-0001": {
        "payload": "<script>alert(2023-5153)</script>",
        "param": "test",
        "affected_versions": ["0.0.0.0.0"],
        "target_url": "/another_vulnerable_page",
    },
}


class XssScanner:
    @staticmethod
    def find_parameters_recursive(base_url, visited_urls=None):
        if visited_urls is None:
            visited_urls = set()

        visited_urls.add(base_url)
        params = set()

        try:
            response = requests.get(base_url)
        except requests.exceptions.InvalidSchema:
            # 비표준 스키마 (예: 'javascript:')를 가진 URL은 건너뛰기
            return params

        soup = BeautifulSoup(response.text, "html.parser")

        # HTML 폼에서 파라미터 수집
        for form in soup.find_all("form"):
            for input_tag in form.find_all("input"):
                param_name = input_tag.get("name") or input_tag.get("id")
                if param_name:
                    params.add(param_name)

        # 직접적으로 input 태그에서 파라미터 수집
        for input_tag in soup.find_all("input"):
            param_name = input_tag.get("name") or input_tag.get("id")
            if param_name:
                params.add(param_name)

        # URL의 쿼리 문자열에서 파라미터 수집
        query_params = parse_qs(urlparse(base_url).query)
        params.update(query_params.keys())

        # 하이퍼링크를 통해 다른 페이지로 이동하면 재귀적으로 파라미터 찾기
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)
            if full_url not in visited_urls:
                params.update(
                    XssScanner.find_parameters_recursive(full_url, visited_urls)
                )

        return params

    @staticmethod
    def scan_url(url, method, cve_data):
        param = cve_data.get("param")
        payload = cve_data.get("payload")
        print(payload)

        if not param or not payload:
            print("[-] 올바른 CVE 데이터가 아닙니다.")
            return

        # 파라미터를 찾지 못한 경우에만 CVE_DATABASE에 있는 payload로 시도
        if param not in XssScanner.find_parameters_recursive(url):
            modified_url = XssScanner.construct_modified_url(url, param, payload)
            print(modified_url)

            if method.upper() == "GET":
                req = requests.get(modified_url)
            elif method.upper() == "POST":
                data = {param: payload}
                req = requests.post(url.split("?")[0], data=data)
            else:
                print("유효하지 않은 HTTP 메소드입니다. GET 또는 POST를 선택해주세요.")
                return

            if req.status_code // 100 == 2:
                if payload in req.text:
                    print(payload)
                    print(
                        f"[+] {url}에서 {param} 파라미터에 {payload}를 사용한 XSS를 발견했습니다."
                    )
                    result = {
                        "name": "Cross-site scripting",
                        "payload": payload,
                        "method": method,
                        "parameter": param,
                        "link": modified_url,
                    }

                    # Detect if the payload matches any CVE entries
                    cve_number = XssScanner.match_cve(payload, param)
                    if cve_number:
                        print(f"[+] CVE 번호: {cve_number}")
                        print(
                            f"[+] 취약한 버전: {', '.join(cve_data['affected_versions'])}"
                        )

                    return result
                else:
                    print("[-] 페이지에 오류가 발생하였습니다.")
                    sys.exit()  # Exit the program

        # 파라미터를 찾지 못했거나 CVE_DATABASE에 있는 payload로 시도한 경우에는 일반 payload로 시도
        for payload in XSS_PAYLOADS:
            modified_url = XssScanner.construct_modified_url(url, param, payload)

            if method.upper() == "GET":
                req = requests.get(modified_url)
            elif method.upper() == "POST":
                data = {param: payload}
                req = requests.post(url.split("?")[0], data=data)
            else:
                print("유효하지 않은 HTTP 메소드입니다. GET 또는 POST를 선택해주세요.")
                return

            if req.status_code // 100 == 2:
                if payload in req.text:
                    print(
                        f"[+] {url}에서 {param} 파라미터에 {payload}를 사용한 XSS를 발견했습니다."
                    )
                    result = {
                        "name": "Cross-site scripting",
                        "payload": payload,
                        "method": method,
                        "parameter": param,
                        "link": modified_url,
                    }
                    return result
                else:
                    print("[-] 페이지에 오류가 발생하였습니다.")
                    sys.exit()  # Exit the program

        print(f"[-] {param} 파라미터에 대한 XSS 취약점을 찾지 못했습니다.")

    @staticmethod
    def match_cve(payload, param):
        for cve_number, cve_data in CVE_DATABASE.items():
            if payload == cve_data["payload"] and param == cve_data.get("param"):
                return cve_number
        return None

    @staticmethod
    def construct_modified_url(url, param, payload):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Check if the parameter already exists in the query
        if param in query_params:
            query_params[param] = [payload]
        else:
            query_params.update({param: [payload]})

        # Combine the modified query parameters with the original URL
        modified_url = urlunparse(
            parsed_url._replace(query=urlencode(query_params, doseq=True))
        )
        return modified_url


def main(url: str, method: str):
    xss_scanner = XssScanner()

    # Convert the provided URL to a normalized form for comparison
    normalized_url = urlparse(url).path

    # Check if the normalized URL matches any entry in CVE_DATABASE
    matched_cve = None
    for cve_number, cve_data in CVE_DATABASE.items():
        if normalized_url == cve_data.get("target_url"):
            matched_cve = cve_data
            break

    if matched_cve:
        print(
            f"[!] 주어진 URL은 취약한 페이지일 수 있습니다. 확인 후 계속 진행하시겠습니까? (Y/N)"
        )
        user_input = input().strip().lower()

        if user_input != "y":
            print("[!] 사용자가 진행을 취소했습니다.")
            return

    for cve_number, cve_data in CVE_DATABASE.items():
        result = xss_scanner.scan_url(url, method, cve_data)

        if result:
            print(cve_number, result.get("payload"))
            xss_report = XssReport(
                url=url,
                is_vuln=True,
                payload=result.get("payload"),
                param=result.get("parameter"),
                data="",
                cve=cve_number,
            )
            xss_report.save()

            print("\n[+] XSS 취약점을 발견하였습니다.")
            print(result)

            break
    else:
        print(
            "\n[-] 현재 파라미터에 대한 XSS 취약점을 찾지 못했습니다. 다음 파라미터로 진행합니다."
        )


if __name__ == "__main__":
    main(url="http://localhost:9001/test_xss?test=test", method="GET")
