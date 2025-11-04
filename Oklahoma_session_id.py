# pip install curl_cffi==0.6.*
from curl_cffi import requests
from pathlib import Path

URL = (
    "https://opa.eclipping.org"
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
    "&date_from=08-03-2025&date_to=11-03-2025&clipping_display_images_server=main"
    "&select_all_pubblication_ids=on&publication_search_filter="
    "&pubblication_ids%5B%5D=2235&pubblication_ids%5B%5D=1781&pubblication_ids%5B%5D=1789"
    "&pubblication_ids%5B%5D=1783&pubblication_ids%5B%5D=1787&pubblication_ids%5B%5D=1785"
    "&pubblication_ids%5B%5D=1791&pubblication_ids%5B%5D=1793&pubblication_ids%5B%5D=1795"
    "&pubblication_ids%5B%5D=1797&pubblication_ids%5B%5D=1801&pubblication_ids%5B%5D=2239"
    "&pubblication_ids%5B%5D=1805&pubblication_ids%5B%5D=2123&pubblication_ids%5B%5D=2273"
    "&pubblication_ids%5B%5D=1803&pubblication_ids%5B%5D=2241&pubblication_ids%5B%5D=2069"
    "&pubblication_ids%5B%5D=1813&pubblication_ids%5B%5D=1815&pubblication_ids%5B%5D=2149"
    "&pubblication_ids%5B%5D=2189&pubblication_ids%5B%5D=1819&pubblication_ids%5B%5D=2263"
    "&pubblication_ids%5B%5D=7651&pubblication_ids%5B%5D=2269&pubblication_ids%5B%5D=1823"
    "&pubblication_ids%5B%5D=1825&pubblication_ids%5B%5D=2537&pubblication_ids%5B%5D=1831"
    "&pubblication_ids%5B%5D=1833&pubblication_ids%5B%5D=12933&pubblication_ids%5B%5D=1835"
    "&pubblication_ids%5B%5D=2733&pubblication_ids%5B%5D=1979&pubblication_ids%5B%5D=1839"
    "&pubblication_ids%5B%5D=1817&pubblication_ids%5B%5D=2243&pubblication_ids%5B%5D=2071"
    "&pubblication_ids%5B%5D=1841&pubblication_ids%5B%5D=1843&pubblication_ids%5B%5D=1775"
    "&pubblication_ids%5B%5D=1845&pubblication_ids%5B%5D=1847&pubblication_ids%5B%5D=1849"
    "&pubblication_ids%5B%5D=1855&pubblication_ids%5B%5D=1851&pubblication_ids%5B%5D=2261"
    "&pubblication_ids%5B%5D=1887&pubblication_ids%5B%5D=2209&pubblication_ids%5B%5D=2133"
    "&pubblication_ids%5B%5D=1997&pubblication_ids%5B%5D=1777&pubblication_ids%5B%5D=1857"
    "&pubblication_ids%5B%5D=1863&pubblication_ids%5B%5D=1865&pubblication_ids%5B%5D=1907"
    "&pubblication_ids%5B%5D=2361&pubblication_ids%5B%5D=1873&pubblication_ids%5B%5D=1989"
    "&pubblication_ids%5B%5D=2125&pubblication_ids%5B%5D=2293&pubblication_ids%5B%5D=1879"
    "&pubblication_ids%5B%5D=1881&pubblication_ids%5B%5D=2113&pubblication_ids%5B%5D=2731"
    "&pubblication_ids%5B%5D=1885&pubblication_ids%5B%5D=13123&pubblication_ids%5B%5D=13102"
    "&pubblication_ids%5B%5D=1889&pubblication_ids%5B%5D=2265&pubblication_ids%5B%5D=1909"
    "&pubblication_ids%5B%5D=1799&pubblication_ids%5B%5D=12435&pubblication_ids%5B%5D=1779"
    "&pubblication_ids%5B%5D=1913&pubblication_ids%5B%5D=5227&pubblication_ids%5B%5D=1837"
    "&pubblication_ids%5B%5D=1915&pubblication_ids%5B%5D=2729&pubblication_ids%5B%5D=1917"
    "&pubblication_ids%5B%5D=2141&pubblication_ids%5B%5D=2267&pubblication_ids%5B%5D=1919"
    "&pubblication_ids%5B%5D=1921&pubblication_ids%5B%5D=2283&pubblication_ids%5B%5D=1923"
    "&pubblication_ids%5B%5D=1925&pubblication_ids%5B%5D=1911&pubblication_ids%5B%5D=1771"
    "&pubblication_ids%5B%5D=1927&pubblication_ids%5B%5D=2271&pubblication_ids%5B%5D=2275"
    "&pubblication_ids%5B%5D=1929&pubblication_ids%5B%5D=1949&pubblication_ids%5B%5D=1953"
    "&pubblication_ids%5B%5D=1821&pubblication_ids%5B%5D=1995&pubblication_ids%5B%5D=2277"
    "&pubblication_ids%5B%5D=1955&pubblication_ids%5B%5D=1957&pubblication_ids%5B%5D=1959"
    "&pubblication_ids%5B%5D=1961&pubblication_ids%5B%5D=1963&pubblication_ids%5B%5D=1807"
    "&pubblication_ids%5B%5D=1965&pubblication_ids%5B%5D=1967&pubblication_ids%5B%5D=1971"
    "&pubblication_ids%5B%5D=1969&pubblication_ids%5B%5D=1975&pubblication_ids%5B%5D=1977"
    "&pubblication_ids%5B%5D=2045&pubblication_ids%5B%5D=1981&pubblication_ids%5B%5D=1985"
    "&pubblication_ids%5B%5D=2279&pubblication_ids%5B%5D=1931&pubblication_ids%5B%5D=2177"
    "&pubblication_ids%5B%5D=1877&pubblication_ids%5B%5D=1991&pubblication_ids%5B%5D=1867"
    "&pubblication_ids%5B%5D=1993&pubblication_ids%5B%5D=2079&pubblication_ids%5B%5D=2171"
    "&pubblication_ids%5B%5D=1999&pubblication_ids%5B%5D=1827&pubblication_ids%5B%5D=2001"
    "&pubblication_ids%5B%5D=1859&pubblication_ids%5B%5D=2003&pubblication_ids%5B%5D=2005"
    "&pubblication_ids%5B%5D=2007&pubblication_ids%5B%5D=2013&pubblication_ids%5B%5D=2015"
    "&pubblication_ids%5B%5D=2281&pubblication_ids%5B%5D=2017&pubblication_ids%5B%5D=1987"
    "&pubblication_ids%5B%5D=1829&pubblication_ids%5B%5D=2285&pubblication_ids%5B%5D=2287"
    "&pubblication_ids%5B%5D=2023&pubblication_ids%5B%5D=2065&pubblication_ids%5B%5D=2289"
    "&pubblication_ids%5B%5D=2291&pubblication_ids%5B%5D=2373&pubblication_ids%5B%5D=2193"
    "&pubblication_ids%5B%5D=2025&pubblication_ids%5B%5D=2027&pubblication_ids%5B%5D=2029"
    "&pubblication_ids%5B%5D=2181&pubblication_ids%5B%5D=2179&pubblication_ids%5B%5D=2183"
    "&pubblication_ids%5B%5D=2299&pubblication_ids%5B%5D=2051&pubblication_ids%5B%5D=2053"
    "&pubblication_ids%5B%5D=2201&pubblication_ids%5B%5D=2055&pubblication_ids%5B%5D=2375"
    "&pubblication_ids%5B%5D=2131&pubblication_ids%5B%5D=2143&pubblication_ids%5B%5D=2565"
    "&pubblication_ids%5B%5D=2589&pubblication_ids%5B%5D=2587&pubblication_ids%5B%5D=2061"
    "&pubblication_ids%5B%5D=2063&pubblication_ids%5B%5D=2073&pubblication_ids%5B%5D=2353"
    "&pubblication_ids%5B%5D=1935&pubblication_ids%5B%5D=2355&pubblication_ids%5B%5D=2371"
    "&pubblication_ids%5B%5D=2357&pubblication_ids%5B%5D=2483&pubblication_ids%5B%5D=2727"
    "&pubblication_ids%5B%5D=2247&pubblication_ids%5B%5D=2067&pubblication_ids%5B%5D=2075"
    "&pubblication_ids%5B%5D=2083&pubblication_ids%5B%5D=2085&pubblication_ids%5B%5D=2105"
    "&pubblication_ids%5B%5D=2087&pubblication_ids%5B%5D=2089&pubblication_ids%5B%5D=2091"
    "&pubblication_ids%5B%5D=2093&pubblication_ids%5B%5D=2095&pubblication_ids%5B%5D=2097"
    "&pubblication_ids%5B%5D=2099&pubblication_ids%5B%5D=2365&pubblication_ids%5B%5D=2101"
    "&pubblication_ids%5B%5D=2103&pubblication_ids%5B%5D=2109&pubblication_ids%5B%5D=1973"
    "&pubblication_ids%5B%5D=2137&pubblication_ids%5B%5D=2111&pubblication_ids%5B%5D=2115"
    "&pubblication_ids%5B%5D=2117&pubblication_ids%5B%5D=2119&pubblication_ids%5B%5D=2121"
    "&pubblication_ids%5B%5D=4095&pubblication_ids%5B%5D=2127&pubblication_ids%5B%5D=2129"
    "&pubblication_ids%5B%5D=1773&pubblication_ids%5B%5D=2367&pubblication_ids%5B%5D=2135"
    "&pubblication_ids%5B%5D=1861&pubblication_ids%5B%5D=4469&pubblication_ids%5B%5D=2191"
    "&pubblication_ids%5B%5D=2481&pubblication_ids%5B%5D=1905&pubblication_ids%5B%5D=2377"
    "&pubblication_ids%5B%5D=1869&pubblication_ids%5B%5D=1871&pubblication_ids%5B%5D=1875"
    "&pubblication_ids%5B%5D=1891&pubblication_ids%5B%5D=2369&pubblication_ids%5B%5D=1893"
    "&pubblication_ids%5B%5D=1895&pubblication_ids%5B%5D=1897&pubblication_ids%5B%5D=1899"
    "&pubblication_ids%5B%5D=1901&pubblication_ids%5B%5D=1903&pubblication_ids%5B%5D=2107"
    "&pubblication_ids%5B%5D=1933&pubblication_ids%5B%5D=2019&pubblication_ids%5B%5D=2363"
    "&pubblication_ids%5B%5D=1809&pubblication_ids%5B%5D=1941&pubblication_ids%5B%5D=1939"
    "&pubblication_ids%5B%5D=2383&pubblication_ids%5B%5D=2385&pubblication_ids%5B%5D=1937"
    "&pubblication_ids%5B%5D=1943&pubblication_ids%5B%5D=2301&pubblication_ids%5B%5D=1945"
    "&pubblication_ids%5B%5D=1947&pubblication_ids%5B%5D=1951&pubblication_ids%5B%5D=2009"
    "&pubblication_ids%5B%5D=2379&pubblication_ids%5B%5D=2011&pubblication_ids%5B%5D=2381"
    "&pubblication_ids%5B%5D=2077&pubblication_ids%5B%5D=2259&pubblication_ids%5B%5D=2021"
    "&pubblication_ids%5B%5D=5707&pubblication_ids%5B%5D=2035&pubblication_ids%5B%5D=2039"
    "&pubblication_ids%5B%5D=2041&pubblication_ids%5B%5D=2295&pubblication_ids%5B%5D=10435"
    "&pubblication_ids%5B%5D=2043&pubblication_ids%5B%5D=2047&pubblication_ids%5B%5D=2173"
    "&pubblication_ids%5B%5D=2037&pubblication_ids%5B%5D=2167&pubblication_ids%5B%5D=5791"
    "&pubblication_ids%5B%5D=2165&pubblication_ids%5B%5D=2169&pubblication_ids%5B%5D=2059"
    "&pubblication_ids%5B%5D=2175&xtext_version="
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
