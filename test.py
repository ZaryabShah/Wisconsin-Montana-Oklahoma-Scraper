# pip install curl_cffi==0.6.*
from curl_cffi import requests

URL = (
    "https://opa.eclipping.org"
    "/eebrowser/bbe/2022032812.pa/public/freesearchtest/search/get-search-results"
    "/format/json"
    "/session_id/9765f8ec89cee2f4bc1d2c869f382e68"
    "/type/legals"
    "/xtext_version/"
    "/clipping_id/"
    "/isMobile/0"
)

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://opa.eclipping.org",
    "referer": "https://opa.eclipping.org/eebrowser/bbe/2022032812.pa/public/freesearchtest/search/index/type/legals/",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "accept-encoding": "gzip, deflate, br, zstd",
}

COOKIES = {
    "PHPSESSID": "c8g13qc27kc59d0c6ihjpbs0bsis6r6f",
    "_ga": "GA1.2.1449247568.1761835612",
    "_gid": "GA1.2.921307114.1761835612",
    "_ga_GDMKX7QJYW": "GS2.2.s1761841243$o2$g1$t1761841251$j52$l0$h0",
}

# Form data from your capture
payload = {
    "sEcho": "1",
    "iColumns": "3",
    "sColumns": "",
    "iDisplayStart": "0",
    "iDisplayLength": "1000",
    "mDataProp_0": "0",
    "mDataProp_1": "1",
    "mDataProp_2": "2",
    "sSearch": "",
    "bRegex": "false",
    "sSearch_0": "",
    "bRegex_0": "false",
    "bSearchable_0": "true",
    "sSearch_1": "",
    "bRegex_1": "false",
    "bSearchable_1": "true",
    "sSearch_2": "",
    "bRegex_2": "false",
    "bSearchable_2": "true",
    "iSortCol_0": "1",
    "sSortDir_0": "desc",
    "iSortingCols": "1",
    "bSortable_0": "true",
    "bSortable_1": "true",
    "bSortable_2": "true",
    "date_from": "08-03-2025",
    "date_to": "",
    "search_terms": "Foreclosure",
    "pubblication_ids": "",
}

def fetch_results():
    with requests.Session(impersonate="chrome120") as s:
        s.headers.update(HEADERS)
        s.cookies.update(COOKIES)
        resp = s.post(URL, data=payload, timeout=30)
        resp.raise_for_status()

        if "application/json" in resp.headers.get("content-type", ""):
            return resp.json()
        return resp.text

if __name__ == "__main__":
    try:
        result = fetch_results()
        with open("output.json", "w", encoding="utf-8") as f:
            if isinstance(result, dict):
                import json
                json.dump(result, f, ensure_ascii=False, indent=2)
            else:
                f.write(result)
        if isinstance(result, dict):
            print("✅ JSON keys:", list(result.keys()))
        else:
            print("✅ Raw response:", result[:500])
    except Exception as e:
        print("❌ Error:", e)
