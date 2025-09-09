import requests
import base64
import re
from controlDB import (
    get_pbn_site_by_url,
)  # 워드프레스 계정정보 불러오기용 (함수명 예시)

# 바꿀 URL
OLD_URL = "365tvda.com"
NEW_URL = "https://365tvda.com/"

# 바꿀 포스트 주소 리스트
post_urls = [
    "https://secondmassage.com//?p=1854",
    "https://jungbomoum.co.kr//?p=2132",
    "https://ppjwc.com//?p=714",
    "https://margiesmassage.com//?p=1985",
    "https://ppjwc.com//?p=718",
    "https://cleanspirit.co.kr//?p=378",
    "https://volantsports.com//?p=1823",
    "https://hvpwc.com//?p=620",
    "https://maihiendidongnghean.com//?p=1938",
    "https://myjungbo.co.kr//?p=761",
    "https://myjungbo.co.kr//?p=763",
    "https://clearmind.ai.kr//?p=1058",
    "https://koreaallinfo.co.kr//?p=492",
    "https://tapsule.me//?p=442",
    "https://koreaallinfo.co.kr//?p=496",
    "https://maihiendidongnghean.com//?p=1944",
    "https://cleanspirit.co.kr//?p=382",
    "https://hugekrblog.co.kr//?p=1337",
    "https://koreaallinfo.co.kr//?p=498",
    "https://uniqecasino.com//?p=1753",
    "https://justlygamble.com//?p=1778",
]


def get_post_id_from_url(url):
    # 주소에서 post id 추출
    m = re.search(r"[?&]p=(\d+)", url)
    return m.group(1) if m else None


def get_domain_from_url(url):
    # 도메인 추출
    m = re.match(r"https?://([^/]+)/", url)
    return m.group(1) if m else None


def get_auth_header(user, app_pass):
    token = f"{user}:{app_pass}"
    b64 = base64.b64encode(token.encode()).decode()
    return {"Authorization": f"Basic {b64}"}


def update_post_content(domain, post_id, auth_header):
    # 1. 기존 포스트 내용 불러오기
    api_url = f"https://{domain}/wp-json/wp/v2/posts/{post_id}"
    res = requests.get(api_url, headers=auth_header)
    if res.status_code != 200:
        print(f"[{domain}] 포스트 {post_id} 불러오기 실패: {res.text}")
        return
    content = res.json()["content"]["rendered"]

    # 2. 앵커텍스트 URL 치환
    new_content = content.replace(OLD_URL, NEW_URL)

    # 3. 내용이 바뀌었으면 업데이트
    if new_content != content:
        update = requests.post(
            api_url,
            headers={**auth_header, "Content-Type": "application/json"},
            json={"content": new_content},
        )
        if update.status_code == 200:
            print(f"[{domain}] 포스트 {post_id} 업데이트 성공")
        else:
            print(f"[{domain}] 포스트 {post_id} 업데이트 실패: {update.text}")
    else:
        print(f"[{domain}] 포스트 {post_id} 변경사항 없음")


def main():
    # 도메인별로 워드프레스 계정정보 불러오기
    domain_auth = {}
    for url in post_urls:
        domain = get_domain_from_url(url)
        if not domain:
            print(f"도메인 추출 실패: {url}")
            continue
        if domain not in domain_auth:
            # controlDB에서 도메인별 계정정보 불러오기 (함수명/구현은 환경에 맞게 수정)
            info = get_pbn_site_by_url(domain)
            if not info:
                print(f"{domain} 계정정보 없음")
                continue
            _, pbn_url, pbn_user, pbn_pass, pbn_app_pass = info
            domain_auth[domain] = get_auth_header(pbn_user, pbn_app_pass)

    # 각 포스트별로 업데이트
    for url in post_urls:
        domain = get_domain_from_url(url)
        post_id = get_post_id_from_url(url)
        if not domain or not post_id:
            print(f"ID/도메인 추출 실패: {url}")
            continue
        if domain not in domain_auth:
            print(f"{domain} 인증정보 없음")
            continue
        update_post_content(domain, post_id, domain_auth[domain])


if __name__ == "__main__":
    main()
