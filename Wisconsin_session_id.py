# pip install curl_cffi==0.6.*
from curl_cffi import requests
from pathlib import Path

URL = (
    "https://wna.eclipping.org"
    "/eebrowser/bbe/2022032812.pa/public//freesearchtest/search/search"
    "/type/legals/format/html"
)

HEADERS = {
    "accept": "text/html, */*; q=0.01",
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
    "PHPSESSID": "3op6of9gq408hi6tr3o10h365kn7el1t",
    "_ga": "GA1.2.484924065.1761774590",
    "_ga_GDMKX7QJYW": "GS2.2.s1761774591$o1$g0$t1761774591$j60$l0$h0",
    "_ga_D12GB1E16S": "GS2.2.s1761935370$o3$g1$t1761935370$j60$l0$h0",
}

# === Exact urlencoded body from your capture (kept as a single line) ===
RAW_BODY = (
    "clipping_id=&terms=Foreclosure&testing_clipping_search_date_range_clone=90"
    "&date_from=08-05-2025&date_to=11-03-2025&clipping_display_images_server=main"
    "&select_all_pubblication_ids=on&publication_search_filter="
    "&pubblication_ids%5B%5D=13399&pubblication_ids%5B%5D=101&pubblication_ids%5B%5D=103"
    "&pubblication_ids%5B%5D=549&pubblication_ids%5B%5D=371&pubblication_ids%5B%5D=373"
    "&pubblication_ids%5B%5D=375&pubblication_ids%5B%5D=377&pubblication_ids%5B%5D=12692"
    "&pubblication_ids%5B%5D=379&pubblication_ids%5B%5D=1753&pubblication_ids%5B%5D=105"
    "&pubblication_ids%5B%5D=587&pubblication_ids%5B%5D=107&pubblication_ids%5B%5D=109"
    "&pubblication_ids%5B%5D=13326&pubblication_ids%5B%5D=13327&pubblication_ids%5B%5D=13328"
    "&pubblication_ids%5B%5D=13329&pubblication_ids%5B%5D=13330&pubblication_ids%5B%5D=10053"
    "&pubblication_ids%5B%5D=381&pubblication_ids%5B%5D=383&pubblication_ids%5B%5D=633"
    "&pubblication_ids%5B%5D=385&pubblication_ids%5B%5D=393&pubblication_ids%5B%5D=10175"
    "&pubblication_ids%5B%5D=635&pubblication_ids%5B%5D=10193&pubblication_ids%5B%5D=6167"
    "&pubblication_ids%5B%5D=115&pubblication_ids%5B%5D=10307&pubblication_ids%5B%5D=10557"
    "&pubblication_ids%5B%5D=10177&pubblication_ids%5B%5D=10179&pubblication_ids%5B%5D=387"
    "&pubblication_ids%5B%5D=4481&pubblication_ids%5B%5D=12461&pubblication_ids%5B%5D=12898"
    "&pubblication_ids%5B%5D=12463&pubblication_ids%5B%5D=117&pubblication_ids%5B%5D=8443"
    "&pubblication_ids%5B%5D=121&pubblication_ids%5B%5D=13310&pubblication_ids%5B%5D=7161"
    "&pubblication_ids%5B%5D=119&pubblication_ids%5B%5D=6351&pubblication_ids%5B%5D=7159"
    "&pubblication_ids%5B%5D=8815&pubblication_ids%5B%5D=123&pubblication_ids%5B%5D=125"
    "&pubblication_ids%5B%5D=127&pubblication_ids%5B%5D=565&pubblication_ids%5B%5D=7069"
    "&pubblication_ids%5B%5D=129&pubblication_ids%5B%5D=6019&pubblication_ids%5B%5D=131"
    "&pubblication_ids%5B%5D=8271&pubblication_ids%5B%5D=133&pubblication_ids%5B%5D=135"
    "&pubblication_ids%5B%5D=13308&pubblication_ids%5B%5D=10181&pubblication_ids%5B%5D=137"
    "&pubblication_ids%5B%5D=389&pubblication_ids%5B%5D=139&pubblication_ids%5B%5D=391"
    "&pubblication_ids%5B%5D=141&pubblication_ids%5B%5D=13305&pubblication_ids%5B%5D=555"
    "&pubblication_ids%5B%5D=395&pubblication_ids%5B%5D=143&pubblication_ids%5B%5D=145"
    "&pubblication_ids%5B%5D=147&pubblication_ids%5B%5D=13315&pubblication_ids%5B%5D=4363"
    "&pubblication_ids%5B%5D=397&pubblication_ids%5B%5D=149&pubblication_ids%5B%5D=10183"
    "&pubblication_ids%5B%5D=10185&pubblication_ids%5B%5D=637&pubblication_ids%5B%5B%5D=10187"
    "&pubblication_ids%5B%5D=13322&pubblication_ids%5B%5D=10189&pubblication_ids%5B%5D=10191"
    "&pubblication_ids%5B%5D=153&pubblication_ids%5B%5D=851&pubblication_ids%5B%5D=399"
    "&pubblication_ids%5B%5D=457&pubblication_ids%5B%5D=401&pubblication_ids%5B%5D=403"
    "&pubblication_ids%5B%5D=405&pubblication_ids%5B%5D=10537&pubblication_ids%5B%5D=407"
    "&pubblication_ids%5B%5D=411&pubblication_ids%5B%5D=413&pubblication_ids%5B%5D=155"
    "&pubblication_ids%5B%5D=595&pubblication_ids%5B%5D=359&pubblication_ids%5B%5D=409"
    "&pubblication_ids%5B%5D=157&pubblication_ids%5B%5D=159&pubblication_ids%5B%5D=415"
    "&pubblication_ids%5B%5D=13280&pubblication_ids%5B%5D=315&pubblication_ids%5B%5D=161"
    "&pubblication_ids%5B%5D=163&pubblication_ids%5B%5D=165&pubblication_ids%5B%5D=13200"
    "&pubblication_ids%5B%5D=169&pubblication_ids%5B%5D=167&pubblication_ids%5B%5D=89"
    "&pubblication_ids%5B%5D=171&pubblication_ids%5B%5D=417&pubblication_ids%5B%5D=173"
    "&pubblication_ids%5B%5D=10311&pubblication_ids%5B%5D=175&pubblication_ids%5B%5D=419"
    "&pubblication_ids%5B%5D=7163&pubblication_ids%5B%5D=7165&pubblication_ids%5B%5D=13372"
    "&pubblication_ids%5B%5D=421&pubblication_ids%5B%5D=7167&pubblication_ids%5B%5D=559"
    "&pubblication_ids%5B%5D=177&pubblication_ids%5B%5D=4073&pubblication_ids%5B%5D=423"
    "&pubblication_ids%5B%5D=425&pubblication_ids%5B%5D=179&pubblication_ids%5B%5D=427"
    "&pubblication_ids%5B%5D=259&pubblication_ids%5B%5D=429&pubblication_ids%5B%5D=563"
    "&pubblication_ids%5B%5D=1751&pubblication_ids%5B%5D=181&pubblication_ids%5B%5D=13406"
    "&pubblication_ids%5B%5D=6207&pubblication_ids%5B%5D=13306&pubblication_ids%5B%5D=183"
    "&pubblication_ids%5B%5D=313&pubblication_ids%5B%5D=185&pubblication_ids%5B%5D=431"
    "&pubblication_ids%5B%5D=433&pubblication_ids%5B%5D=8943&pubblication_ids%5B%5D=435"
    "&pubblication_ids%5B%5D=10695&pubblication_ids%5B%5D=583&pubblication_ids%5B%5D=593"
    "&pubblication_ids%5B%5D=437&pubblication_ids%5B%5D=187&pubblication_ids%5B%5D=439"
    "&pubblication_ids%5B%5D=13319&pubblication_ids%5B%5D=189&pubblication_ids%5B%5D=5973"
    "&pubblication_ids%5B%5D=215&pubblication_ids%5B%5D=193&pubblication_ids%5B%5D=669"
    "&pubblication_ids%5B%5D=8765&pubblication_ids%5B%5D=12445&pubblication_ids%5B%5D=195"
    "&pubblication_ids%5B%5D=441&pubblication_ids%5B%5D=13408&pubblication_ids%5B%5D=13299"
    "&pubblication_ids%5B%5D=12659&pubblication_ids%5B%5D=13281&pubblication_ids%5B%5D=585"
    "&pubblication_ids%5B%5D=12495&pubblication_ids%5B%5D=13303&pubblication_ids%5B%5D=10309"
    "&pubblication_ids%5B%5D=197&pubblication_ids%5B%5D=199&pubblication_ids%5B%5D=201"
    "&pubblication_ids%5B%5D=443&pubblication_ids%5B%5D=573&pubblication_ids%5B%5D=597"
    "&pubblication_ids%5B%5D=571&pubblication_ids%5B%5D=13295&pubblication_ids%5B%5D=203"
    "&pubblication_ids%5B%5D=6021&pubblication_ids%5B%5D=8475&pubblication_ids%5B%5D=347"
    "&pubblication_ids%5B%5D=205&pubblication_ids%5B%5D=207&pubblication_ids%5B%5D=445"
    "&pubblication_ids%5B%5D=13313&pubblication_ids%5B%5D=191&pubblication_ids%5B%5D=13405"
    "&pubblication_ids%5B%5D=543&pubblication_ids%5B%5D=447&pubblication_ids%5B%5D=13350"
    "&pubblication_ids%5B%5D=13311&pubblication_ids%5B%5D=6023&pubblication_ids%5B%5D=209"
    "&pubblication_ids%5B%5D=13244&pubblication_ids%5B%5D=213&pubblication_ids%5B%5D=449"
    "&pubblication_ids%5B%5D=217&pubblication_ids%5B%5D=8945&pubblication_ids%5B%5D=91"
    "&pubblication_ids%5B%5D=589&pubblication_ids%5B%5D=653&pubblication_ids%5B%5D=553"
    "&pubblication_ids%5B%5D=557&pubblication_ids%5B%5D=6591&pubblication_ids%5B%5D=569"
    "&pubblication_ids%5B%5D=649&pubblication_ids%5B%5D=581&pubblication_ids%5B%5D=10539"
    "&pubblication_ids%5B%5D=651&pubblication_ids%5B%5D=8819&pubblication_ids%5B%5D=611"
    "&pubblication_ids%5B%5D=567&pubblication_ids%5B%5D=7517&pubblication_ids%5B%5D=10267"
    "&pubblication_ids%5B%5D=221&pubblication_ids%5B%5D=451&pubblication_ids%5B%5D=453"
    "&pubblication_ids%5B%5D=13314&pubblication_ids%5B%5D=12693&pubblication_ids%5B%5D=455"
    "&pubblication_ids%5B%5D=639&pubblication_ids%5B%5D=225&pubblication_ids%5B%5D=13401"
    "&pubblication_ids%5B%5D=227&pubblication_ids%5B%5D=459&pubblication_ids%5B%5D=8817"
    "&pubblication_ids%5B%5D=13302&pubblication_ids%5B%5D=229&pubblication_ids%5B%5D=461"
    "&pubblication_ids%5B%5D=561&pubblication_ids%5B%5D=231&pubblication_ids%5B%5D=577"
    "&pubblication_ids%5B%5D=8445&pubblication_ids%5B%5D=463&pubblication_ids%5B%5D=4475"
    "&pubblication_ids%5B%5D=4477&pubblication_ids%5B%5D=8941&pubblication_ids%5B%5D=4473"
    "&pubblication_ids%5B%5D=579&pubblication_ids%5B%5D=235&pubblication_ids%5B%5D=8273"
    "&pubblication_ids%5B%5D=257&pubblication_ids%5B%5D=6717&pubblication_ids%5B%5D=575"
    "&pubblication_ids%5B%5D=8269&pubblication_ids%5B%5D=8267&pubblication_ids%5B%5D=233"
    "&pubblication_ids%5B%5D=8195&pubblication_ids%5B%5D=237&pubblication_ids%5B%5D=239"
    "&pubblication_ids%5B%5D=465&pubblication_ids%5B%5D=10729&pubblication_ids%5B%5D=13309"
    "&pubblication_ids%5B%5D=241&pubblication_ids%5B%5D=243&pubblication_ids%5B%5D=467"
    "&pubblication_ids%5B%5D=245&pubblication_ids%5B%5D=247&pubblication_ids%5B%5D=10521"
    "&pubblication_ids%5B%5D=469&pubblication_ids%5B%5D=249&pubblication_ids%5B%5D=12391"
    "&pubblication_ids%5B%5D=7197&pubblication_ids%5B%5D=251&pubblication_ids%5B%5D=10195"
    "&pubblication_ids%5B%5D=253&pubblication_ids%5B%5D=13323&pubblication_ids%5B%5D=4361"
    "&pubblication_ids%5B%5D=5999&pubblication_ids%5B%5D=339&pubblication_ids%5B%5D=2617"
    "&pubblication_ids%5B%5D=255&pubblication_ids%5B%5D=13317&pubblication_ids%5B%5D=12694"
    "&pubblication_ids%5B%5D=261&pubblication_ids%5B%5D=263&pubblication_ids%5B%5D=471"
    "&pubblication_ids%5B%5D=473&pubblication_ids%5B%5D=475&pubblication_ids%5B%5D=265"
    "&pubblication_ids%5B%5D=12588&pubblication_ids%5B%5D=267&pubblication_ids%5B%5D=269"
    "&pubblication_ids%5B%5D=2607&pubblication_ids%5B%5D=477&pubblication_ids%5B%5D=10697"
    "&pubblication_ids%5B%5D=479&pubblication_ids%5B%5D=10967&pubblication_ids%5B%5D=271"
    "&pubblication_ids%5B%5D=4419&pubblication_ids%5B%5D=12636&pubblication_ids%5B%5D=8949"
    "&pubblication_ids%5B%5D=7033&pubblication_ids%5B%5D=5209&pubblication_ids%5B%5D=6203"
    "&pubblication_ids%5B%5D=273&pubblication_ids%5B%5D=481&pubblication_ids%5B%5D=4411"
    "&pubblication_ids%5B%5D=483&pubblication_ids%5B%5D=591&pubblication_ids%5B%5D=5983"
    "&pubblication_ids%5B%5D=275&pubblication_ids%5B%5D=485&pubblication_ids%5B%5D=487"
    "&pubblication_ids%5B%5D=513&pubblication_ids%5B%5D=641&pubblication_ids%5B%5D=489"
    "&pubblication_ids%5B%5D=5977&pubblication_ids%5B%5D=5979&pubblication_ids%5B%5D=279"
    "&pubblication_ids%5B%5D=491&pubblication_ids%5B%5D=493&pubblication_ids%5B%5D=281"
    "&pubblication_ids%5B%5D=13282&pubblication_ids%5B%5D=10197&pubblication_ids%5B%5D=10199"
    "&pubblication_ids%5B%5D=283&pubblication_ids%5B%5D=10241&pubblication_ids%5B%5D=285"
    "&pubblication_ids%5B%5D=655&pubblication_ids%5B%5D=13367&pubblication_ids%5B%5D=289"
    "&pubblication_ids%5B%5D=5907&pubblication_ids%5B%5D=291&pubblication_ids%5B%5D=13312"
    "&pubblication_ids%5B%5D=293&pubblication_ids%5B%5D=13304&pubblication_ids%5B%5D=81"
    "&pubblication_ids%5B%5D=295&pubblication_ids%5B%5D=299&pubblication_ids%5B%5D=645"
    "&pubblication_ids%5B%5D=551&pubblication_ids%5B%5D=9583&pubblication_ids%5B%5D=9585"
    "&pubblication_ids%5B%5D=495&pubblication_ids%5B%5D=497&pubblication_ids%5B%5D=499"
    "&pubblication_ids%5B%5D=12672&pubblication_ids%5B%5D=501&pubblication_ids%5B%5D=13320"
    "&pubblication_ids%5B%5D=4479&pubblication_ids%5B%5D=503&pubblication_ids%5B%5D=505"
    "&pubblication_ids%5B%5D=6305&pubblication_ids%5B%5D=303&pubblication_ids%5B%5D=305"
    "&pubblication_ids%5B%5D=11541&pubblication_ids%5B%5D=307&pubblication_ids%5B%5D=507"
    "&pubblication_ids%5B%5D=13262&pubblication_ids%5B%5D=509&pubblication_ids%5B%5D=13318"
    "&pubblication_ids%5B%5D=12642&pubblication_ids%5B%5D=12853&pubblication_ids%5B%5D=511"
    "&pubblication_ids%5B%5D=309&pubblication_ids%5B%5D=515&pubblication_ids%5B%5D=517"
    "&pubblication_ids%5B%5D=13163&pubblication_ids%5B%5D=311&pubblication_ids%5B%5D=13307"
    "&pubblication_ids%5B%5D=519&pubblication_ids%5B%5D=317&pubblication_ids%5B%5D=319"
    "&pubblication_ids%5B%5D=321&pubblication_ids%5B%5D=13296&pubblication_ids%5B%5D=13294"
    "&pubblication_ids%5B%5D=521&pubblication_ids%5B%5D=6197&pubblication_ids%5B%5D=10201"
    "&pubblication_ids%5B%5D=6201&pubblication_ids%5B%5D=523&pubblication_ids%5B%5D=323"
    "&pubblication_ids%5B%5D=325&pubblication_ids%5B%5D=327&pubblication_ids%5B%5D=11055"
    "&pubblication_ids%5B%5D=6205&pubblication_ids%5B%5D=8947&pubblication_ids%5B%5D=329"
    "&pubblication_ids%5B%5D=331&pubblication_ids%5B%5D=525&pubblication_ids%5B%5D=333"
    "&pubblication_ids%5B%5D=10203&pubblication_ids%5B%5D=211&pubblication_ids%5B%5D=337"
    "&pubblication_ids%5B%5D=301&pubblication_ids%5B%5D=335&pubblication_ids%5B%5D=527"
    "&pubblication_ids%5B%5D=13349&pubblication_ids%5B%5D=13324&pubblication_ids%5B%5D=341"
    "&pubblication_ids%5B%5D=12465&pubblication_ids%5B%5D=12467&pubblication_ids%5B%5D=353"
    "&pubblication_ids%5B%5D=12469&pubblication_ids%5B%5D=5981&pubblication_ids%5B%5D=529"
    "&pubblication_ids%5B%5D=12697&pubblication_ids%5B%5D=13331&pubblication_ids%5B%5D=13199"
    "&pubblication_ids%5B%5D=601&pubblication_ids%5B%5D=531&pubblication_ids%5B%5D=343"
    "&pubblication_ids%5B%5D=13321&pubblication_ids%5B%5D=345&pubblication_ids%5B%5D=349"
    "&pubblication_ids%5B%5D=13407&pubblication_ids%5B%5D=533&pubblication_ids%5B%5D=1755"
    "&pubblication_ids%5B%5D=6199&pubblication_ids%5B%5D=8991&pubblication_ids%5B%5D=13298"
    "&pubblication_ids%5B%5D=13297&pubblication_ids%5B%5D=535&pubblication_ids%5B%5D=537"
    "&pubblication_ids%5B%5D=647&pubblication_ids%5B%5D=6173&pubblication_ids%5B%5D=12696"
    "&pubblication_ids%5B%5D=539&pubblication_ids%5B%5D=599&pubblication_ids%5B%5D=7169"
    "&pubblication_ids%5B%5D=355&pubblication_ids%5B%5D=541&pubblication_ids%5B%5D=12695"
    "&pubblication_ids%5B%5D=357&pubblication_ids%5B%5D=11295&pubblication_ids%5B%5D=8477"
    "&xtext_version="
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
