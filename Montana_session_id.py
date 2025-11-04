# pip install curl_cffi==0.6.*
from curl_cffi import requests
from pathlib import Path

URL = (
    "https://www.montanapublicnotices.com"
    "/eebrowser/bbe/2022032812.pa/public//freesearchtest/search/search"
    "/type/legals/format/html"
)

HEADERS = {
    "accept": "text/html, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.montanapublicnotices.com",
    "referer": "https://www.montanapublicnotices.com/eebrowser/bbe/2022032812.pa/public/freesearchtest/search/index/type/legals/",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "accept-encoding": "gzip, deflate, br, zstd",
}

COOKIES = {
    "PHPSESSID": "3op6of9gq408hi6tr3o10h365kn7el1t",
    "_ga": "GA1.2.484924065.1761774590",
    "_ga_GDMKX7QJYW": "GS2.2.s1761774591$o1$g0$t1761774591$j60$l0$h0",
    "_ga_D12GB1E16S": "GS2.2.s1761935370$o3$g1$t1761935370$j60$l0$h0",
}

# === Exact urlencoded body from your capture (kept as a single line) ===
RAW_BODY =(
    "clipping_id=&terms=Foreclosure&testing_clipping_search_date_range_clone=90"
    "&date_from=08-03-2025&date_to=11-03-2025&clipping_display_images_server=chbbe04"
    "&select_all_pubblication_ids=on&publication_search_filter="
    "&pubblication_ids%5B%5D=4969&pubblication_ids%5B%5D=4973&pubblication_ids%5B%5D=5089"
    "&pubblication_ids%5B%5D=4975&pubblication_ids%5B%5D=4981&pubblication_ids%5B%5D=4983"
    "&pubblication_ids%5B%5D=4985&pubblication_ids%5B%5D=5173&pubblication_ids%5B%5D=5129"
    "&pubblication_ids%5B%5D=5017&pubblication_ids%5B%5D=5001&pubblication_ids%5B%5D=5003"
    "&pubblication_ids%5B%5D=12317&pubblication_ids%5B%5D=5183&pubblication_ids%5B%5D=5795"
    "&pubblication_ids%5B%5D=5151&pubblication_ids%5B%5D=5013&pubblication_ids%5B%5D=5143"
    "&pubblication_ids%5B%5D=5019&pubblication_ids%5B%5D=5213&pubblication_ids%5B%5D=5145"
    "&pubblication_ids%5B%5D=10399&pubblication_ids%5B%5D=5065&pubblication_ids%5B%5D=5101"
    "&pubblication_ids%5B%5D=5157&pubblication_ids%5B%5D=5069&pubblication_ids%5B%5D=5071"
    "&pubblication_ids%5B%5D=4977&pubblication_ids%5B%5D=5005&pubblication_ids%5B%5D=5077"
    "&pubblication_ids%5B%5D=4971&pubblication_ids%5B%5D=5103&pubblication_ids%5B%5D=5009"
    "&pubblication_ids%5B%5D=5083&pubblication_ids%5B%5D=5085&pubblication_ids%5B%5D=5021"
    "&pubblication_ids%5B%5D=5093&pubblication_ids%5B%5D=5195&pubblication_ids%5B%5D=5023"
    "&pubblication_ids%5B%5D=5079&pubblication_ids%5B%5D=5095&pubblication_ids%5B%5D=5061"
    "&pubblication_ids%5B%5D=5099&pubblication_ids%5B%5D=5171&pubblication_ids%5B%5D=5123"
    "&pubblication_ids%5B%5D=5149&pubblication_ids%5B%5D=5107&pubblication_ids%5B%5D=5109"
    "&pubblication_ids%5B%5D=5015&pubblication_ids%5B%5D=5131&pubblication_ids%5B%5D=4979"
    "&pubblication_ids%5B%5D=5073&pubblication_ids%5B%5D=5189&pubblication_ids%5B%5D=5135"
    "&pubblication_ids%5B%5D=5175&pubblication_ids%5B%5D=5137&pubblication_ids%5B%5D=5139"
    "&pubblication_ids%5B%5D=6623&pubblication_ids%5B%5D=5141&pubblication_ids%5B%5D=5211"
    "&pubblication_ids%5B%5D=10727&pubblication_ids%5B%5D=5011&pubblication_ids%5B%5D=5125"
    "&pubblication_ids%5B%5D=10121&pubblication_ids%5B%5D=5215&pubblication_ids%5B%5D=5133"
    "&pubblication_ids%5B%5D=5007&pubblication_ids%5B%5D=5087&pubblication_ids%5B%5D=5081"
    "&pubblication_ids%5B%5D=5167&pubblication_ids%5B%5D=5155&pubblication_ids%5B%5D=5179"
    "&pubblication_ids%5B%5D=5063&pubblication_ids%5B%5D=5163&pubblication_ids%5B%5D=5165"
    "&pubblication_ids%5B%5D=5147&pubblication_ids%5B%5D=5169&pubblication_ids%5B%5D=5067"
    "&pubblication_ids%5B%5D=5025&pubblication_ids%5B%5D=5177&pubblication_ids%5B%5D=5181"
    "&pubblication_ids%5B%5D=5091&pubblication_ids%5B%5D=5075&pubblication_ids%5B%5D=5185"
    "&pubblication_ids%5B%5D=5153&pubblication_ids%5B%5D=5105&pubblication_ids%5B%5D=5187"
    "&pubblication_ids%5B%5D=8435&pubblication_ids%5B%5D=10923&pubblication_ids%5B%5D=5127"
    "&pubblication_ids%5B%5D=5191&pubblication_ids%5B%5D=5193&pubblication_ids%5B%5D=4951"
    "&pubblication_ids%5B%5D=5097&xtext_version="
)

OUTFILE = Path("search_results.html")

def run_post():
    with requests.Session(impersonate="chrome120") as s:
        s.headers.update(HEADERS)
        s.cookies.update(COOKIES)
        # Send the exact raw urlencoded body
        resp = s.post(URL, data=RAW_BODY, timeout=60)
        resp.raise_for_status()

        html = resp.text  # curl_cffi auto-decompresses gzip/br/zstd
        OUTFILE.write_text(html, encoding="utf-8")
        print("✅ Status:", resp.status_code)
        print("✅ Content-Type:", resp.headers.get("content-type"))
        print("✅ Saved to:", OUTFILE.resolve())
        print("🔎 Preview:", html[:400])

if __name__ == "__main__":
    run_post()
