#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고도화된 PBN 시스템 테스트 스크립트
디버깅 및 단계별 검증을 위한 테스트 도구
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_main_v2 import EnhancedPBNSystem
from controlDB import (
    get_active_clients,
    get_all_pbn_sites,
    get_random_keyword_for_client,
)


async def test_content_generation():
    """콘텐츠 생성 테스트"""
    print("🧪 콘텐츠 생성 테스트 시작")
    print("=" * 50)

    # 시스템 초기화
    system = EnhancedPBNSystem()

    # 테스트용 키워드
    test_keyword = "백링크 테스트"

    # 가상의 클라이언트 튜플 (실제 DB에서 가져오는 것과 동일한 구조)
    test_client = (
        999,
        "테스트 클라이언트",
        "https://test-client.com",
        None,
        None,
        None,
        None,
        None,
        None,
    )

    # 가상의 PBN 사이트 (실제로는 사용하지 않음)
    test_pbn = (1, "https://test-pbn.com", "test_user", "test_pass", "test_app_pass")

    print(f"🔍 테스트 키워드: {test_keyword}")
    print(f"👤 테스트 클라이언트: {test_client[1]}")
    print()

    try:
        # 콘텐츠 생성
        print("📝 콘텐츠 생성 중...")
        content = await system.generate_enhanced_content(
            test_client, test_keyword, test_pbn
        )

        if content:
            print("✅ 콘텐츠 생성 성공!")
            print(f"   📊 제목: {content['title']}")
            print(f"   📊 단어 수: {content['statistics']['total_word_count']}")
            print(f"   📊 섹션 수: {content['statistics']['total_sections']}")
            print(f"   📊 SEO 점수: {content['statistics']['seo_score']}")

            # 생성된 파일들 확인
            print("\n📁 생성된 디버깅 파일들:")
            debug_dir = Path("data")
            if debug_dir.exists():
                for file in debug_dir.glob(f"*{test_keyword.replace(' ', '_')}*"):
                    print(f"   📄 {file.name}")

            return True
        else:
            print("❌ 콘텐츠 생성 실패")
            return False

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_wordpress_connection():
    """워드프레스 연결 테스트"""
    print("\n🔗 워드프레스 연결 테스트")
    print("=" * 50)

    # 실제 PBN 사이트가 있는지 확인
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

    try:
        from wordpress_functions import WordPressManager

        wp_manager = WordPressManager()

        # 간단한 테스트 포스트 생성
        test_title = f"연결 테스트 {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_content = "<p>이것은 연결 테스트용 포스트입니다.</p>"

        print("📤 테스트 포스트 업로드 중...")
        result = wp_manager.create_post(
            site_url=pbn_url,
            username=pbn_user,
            app_password=pbn_app_pass,  # REST API용 앱 패스워드 사용
            title=test_title,
            content=test_content,
            status="draft",  # 초안으로 생성
        )

        if result:
            print(f"✅ 워드프레스 연결 성공! 포스트 ID: {result}")
            return True
        else:
            print("❌ 워드프레스 연결 실패")
            return False

    except Exception as e:
        print(f"❌ 워드프레스 연결 테스트 중 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_connection():
    """데이터베이스 연결 테스트"""
    print("\n🗄️ 데이터베이스 연결 테스트")
    print("=" * 50)

    try:
        # 활성 클라이언트 조회
        active_clients = get_active_clients()
        print(f"👥 활성 클라이언트 수: {len(active_clients)}")

        # PBN 사이트 조회
        pbn_sites = get_all_pbn_sites()
        print(f"🌐 PBN 사이트 수: {len(pbn_sites)}")

        if active_clients:
            # 첫 번째 클라이언트의 키워드 조회
            client_id = active_clients[0][0]
            keywords = get_random_keyword_for_client(client_id)
            print(f"🔑 클라이언트 {client_id}의 키워드: {keywords}")

        print("✅ 데이터베이스 연결 성공")
        return True

    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False


async def main():
    """메인 테스트 함수"""
    print("🚀 고도화된 PBN 시스템 종합 테스트")
    print("=" * 60)

    # 1. 데이터베이스 연결 테스트
    db_success = test_database_connection()

    # 2. 콘텐츠 생성 테스트
    content_success = await test_content_generation()

    # 3. 워드프레스 연결 테스트
    wp_success = await test_wordpress_connection()

    # 결과 요약
    print("\n📊 테스트 결과 요약")
    print("=" * 50)
    print(f"🗄️ 데이터베이스: {'✅ 성공' if db_success else '❌ 실패'}")
    print(f"📝 콘텐츠 생성: {'✅ 성공' if content_success else '❌ 실패'}")
    print(f"🔗 워드프레스: {'✅ 성공' if wp_success else '❌ 실패'}")

    if all([db_success, content_success, wp_success]):
        print("\n🎉 모든 테스트 통과! 시스템이 정상적으로 작동합니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 위의 오류 메시지를 확인하세요.")

    print("\n📁 생성된 디버깅 파일들을 data/ 폴더에서 확인하세요.")


if __name__ == "__main__":
    asyncio.run(main())
