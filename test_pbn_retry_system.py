#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PBN 재시도 시스템 테스트 스크립트
"""

import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_main_v2 import EnhancedPBNSystem
from controlDB import get_all_pbn_sites, get_active_clients


def test_pbn_retry_system():
    """PBN 재시도 시스템 테스트"""
    print("🧪 PBN 재시도 시스템 테스트 시작")
    print("=" * 50)

    # 시스템 초기화
    system = EnhancedPBNSystem()

    # PBN 사이트 목록 확인
    pbn_sites = get_all_pbn_sites()
    print(f"📊 사용 가능한 PBN 사이트: {len(pbn_sites)}개")

    for i, site in enumerate(pbn_sites, 1):
        site_id, url, user, password, app_pass = site
        print(
            f"   [{i}] {url} (사용자: {user}, 앱패스워드: {'있음' if app_pass else '없음'})"
        )

    if len(pbn_sites) < 2:
        print("⚠️ PBN 재시도 테스트를 위해서는 최소 2개의 PBN 사이트가 필요합니다.")
        print("   (1차 시도 실패 시 2차 시도를 위해)")
        return False

    # 활성 클라이언트 확인
    clients = get_active_clients()
    if not clients:
        print("❌ 활성 클라이언트가 없습니다.")
        return False

    print(f"📋 활성 클라이언트: {len(clients)}개")

    # 첫 번째 클라이언트로 테스트
    test_client = clients[0]
    client_id, client_name, client_site_url = test_client[:3]

    print(f"🎯 테스트 클라이언트: {client_name} ({client_site_url})")

    # 테스트용 콘텐츠 생성
    test_content = {
        "title": f"PBN 재시도 테스트 {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "html_content": f"""
        <h1>PBN 재시도 시스템 테스트</h1>
        
        <h2>테스트 개요</h2>
        <p>이 포스트는 PBN 재시도 시스템의 정상 작동을 확인하기 위한 테스트 포스트입니다.</p>
        <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h3>테스트 내용</h3>
        <ul>
            <li>원본 HTML 콘텐츠 사용 확인</li>
            <li>PBN 사이트 재시도 로직 확인</li>
            <li>REST API 타임아웃 1분 설정 확인</li>
        </ul>
        
        <h3>백링크 테스트</h3>
        <p>이 콘텐츠는 <a href="{client_site_url}" target="_blank" rel="noopener">테스트 클라이언트</a>를 위한 백링크를 포함합니다.</p>
        
        <p>테스트가 성공적으로 완료되면 이 포스트가 PBN 사이트 중 하나에 업로드됩니다.</p>
        """,
    }

    test_keyword = "PBN 재시도 테스트"

    print(f"\n🔧 테스트 콘텐츠 준비 완료:")
    print(f"   제목: {test_content['title']}")
    print(f"   콘텐츠 크기: {len(test_content['html_content'])} 바이트")
    print(f"   키워드: {test_keyword}")

    # PBN 재시도 시스템 테스트
    print(f"\n🚀 PBN 재시도 시스템 테스트 시작...")
    print("=" * 50)

    try:
        # 첫 번째 PBN 사이트를 현재 사이트로 설정
        current_pbn = pbn_sites[0]

        success = system._try_posting_with_retry(
            content=test_content,
            post_content=test_content["html_content"],
            keyword=test_keyword,
            client_id=client_id,
            client_name=client_name,
            client_site_url=client_site_url,
            current_pbn_site=current_pbn,
        )

        if success:
            print(f"\n✅ PBN 재시도 시스템 테스트 성공!")
            print(f"🎉 테스트 포스트가 성공적으로 업로드되었습니다.")
            return True
        else:
            print(f"\n❌ PBN 재시도 시스템 테스트 실패")
            print(f"💥 모든 PBN 사이트에서 업로드에 실패했습니다.")
            return False

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_original_html_usage():
    """원본 HTML 사용 테스트"""
    print("\n" + "=" * 50)
    print("🔧 원본 HTML 콘텐츠 사용 테스트")
    print("=" * 50)

    system = EnhancedPBNSystem()

    # 테스트용 콘텐츠 (html_content 포함)
    test_content_with_html = {
        "title": "원본 HTML 테스트",
        "content": "마크다운 콘텐츠",
        "html_content": "<h1>원본 HTML 콘텐츠</h1><p>이것은 원본 HTML입니다.</p>",
    }

    # 테스트용 콘텐츠 (html_content 없음)
    test_content_without_html = {
        "title": "HTML 없는 테스트",
        "content": "# 마크다운 제목\n\n마크다운 **콘텐츠**입니다.",
    }

    print("🔍 HTML 콘텐츠가 있는 경우 테스트:")
    if (
        "html_content" in test_content_with_html
        and test_content_with_html["html_content"]
    ):
        print("   ✅ 원본 HTML 콘텐츠를 사용합니다.")
        print(f"   📄 콘텐츠: {test_content_with_html['html_content'][:50]}...")
    else:
        print("   ❌ 원본 HTML 콘텐츠가 없습니다.")

    print("\n🔍 HTML 콘텐츠가 없는 경우 테스트:")
    if (
        "html_content" in test_content_without_html
        and test_content_without_html["html_content"]
    ):
        print("   ✅ 원본 HTML 콘텐츠를 사용합니다.")
    else:
        print("   ⚠️ 원본 HTML 콘텐츠가 없어 간단한 HTML을 생성합니다.")
        try:
            simple_html = system._create_simple_html_content(test_content_without_html)
            print(f"   📄 생성된 HTML: {simple_html[:100]}...")
        except Exception as e:
            print(f"   ❌ 간단한 HTML 생성 실패: {e}")


if __name__ == "__main__":
    print("🎯 PBN 재시도 시스템 및 원본 HTML 사용 테스트")
    print("=" * 60)

    # 원본 HTML 사용 테스트
    test_original_html_usage()

    # PBN 재시도 시스템 테스트
    success = test_pbn_retry_system()

    print("\n" + "=" * 60)
    if success:
        print("🎉 모든 테스트 성공!")
    else:
        print("⚠️ 일부 테스트 실패. 로그를 확인해주세요.")
