#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드프레스 REST API 테스트 스크립트
"""

import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wordpress_functions import WordPressManager
from controlDB import get_all_pbn_sites


def test_wordpress_restapi():
    """워드프레스 REST API 테스트"""
    print("🔗 워드프레스 REST API 테스트 시작")
    print("=" * 50)

    # PBN 사이트 조회
    pbn_sites = get_all_pbn_sites()
    if not pbn_sites:
        print("❌ PBN 사이트가 없습니다. 먼저 PBN 사이트를 추가하세요.")
        return False

    print(f"📊 총 {len(pbn_sites)}개의 PBN 사이트 발견")

    # 첫 번째 PBN 사이트로 테스트
    pbn_site = pbn_sites[0]
    pbn_site_id, pbn_url, pbn_user, pbn_pass, pbn_app_pass = pbn_site

    print(f"🌐 테스트 대상: {pbn_url}")
    print(f"👤 사용자: {pbn_user}")
    print(f"🔑 앱 패스워드: {'*' * len(pbn_app_pass) if pbn_app_pass else 'None'}")

    if not pbn_app_pass:
        print(
            "❌ 앱 패스워드가 없습니다. REST API 사용을 위해 앱 패스워드가 필요합니다."
        )
        return False

    try:
        wp_manager = WordPressManager()

        # 테스트 포스트 생성
        test_title = f"REST API 테스트 {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_content = """
        <h2>REST API 테스트</h2>
        <p>이것은 REST API를 통해 생성된 테스트 포스트입니다.</p>
        <ul>
            <li>생성 시간: {}</li>
            <li>API 방식: WordPress REST API</li>
            <li>상태: 테스트</li>
        </ul>
        <p>이 포스트는 테스트 목적으로 생성되었습니다.</p>
        """.format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        print("📤 REST API로 테스트 포스트 업로드 중...")
        result = wp_manager.create_post(
            site_url=pbn_url,
            username=pbn_user,
            app_password=pbn_app_pass,
            title=test_title,
            content=test_content,
            status="draft",  # 초안으로 생성
        )

        if result:
            print(f"✅ REST API 테스트 성공!")
            print(f"📝 생성된 포스트 ID: {result}")
            print(f"🔗 포스트 URL: {pbn_url}/?p={result}")
            return True
        else:
            print("❌ REST API 테스트 실패")
            return False

    except Exception as e:
        print(f"❌ REST API 테스트 중 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_wordpress_restapi()

    print("\n" + "=" * 50)
    if success:
        print("🎉 REST API 테스트 완료! 시스템이 정상적으로 작동합니다.")
    else:
        print("⚠️ REST API 테스트 실패. 설정을 확인해주세요.")
        print("\n확인사항:")
        print("1. PBN 사이트의 앱 패스워드가 올바르게 설정되어 있는지")
        print("2. 워드프레스 사이트가 정상적으로 접근 가능한지")
        print("3. REST API가 활성화되어 있는지")
