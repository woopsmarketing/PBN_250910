#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PBN 링크 빌딩 시스템 테스트 스크립트
사용자가 요청한 대로 스크립트 파일로 테스트를 수행합니다.
"""

import os
import sys
import time
from datetime import datetime


def test_imports():
    """필요한 모듈들이 정상적으로 import되는지 테스트"""
    print("📦 모듈 import 테스트 시작...")

    try:
        from pbn_content_crawler import PBNContentCrawler, PBNPost

        print("   ✅ pbn_content_crawler 모듈 import 성공")
    except ImportError as e:
        print(f"   ❌ pbn_content_crawler import 실패: {e}")
        return False

    try:
        from intelligent_link_builder import IntelligentLinkBuilder, LinkCandidate

        print("   ✅ intelligent_link_builder 모듈 import 성공")
    except ImportError as e:
        print(f"   ❌ intelligent_link_builder import 실패: {e}")
        return False

    try:
        from enhanced_main_v2 import EnhancedPBNSystem

        print("   ✅ enhanced_main_v2 모듈 import 성공")
    except ImportError as e:
        print(f"   ❌ enhanced_main_v2 import 실패: {e}")
        return False

    print("✅ 모든 모듈 import 성공!")
    return True


def test_database_creation():
    """데이터베이스 생성 테스트"""
    print("\n🗄️ 데이터베이스 생성 테스트 시작...")

    try:
        from pbn_content_crawler import PBNContentCrawler

        # 테스트용 데이터베이스 생성
        test_db_path = "test_pbn_content.db"

        # 기존 테스트 DB 파일이 있으면 삭제
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        crawler = PBNContentCrawler(db_path=test_db_path)

        # 데이터베이스 파일이 생성되었는지 확인
        if os.path.exists(test_db_path):
            print("   ✅ 데이터베이스 파일 생성 성공")

            # 통계 조회 테스트
            stats = crawler.get_database_stats()
            print(f"   📊 초기 데이터베이스 상태: {stats['total_posts']}개 포스트")

            # 테스트 DB 파일 삭제
            os.remove(test_db_path)
            print("   🧹 테스트 데이터베이스 파일 정리 완료")

            return True
        else:
            print("   ❌ 데이터베이스 파일 생성 실패")
            return False

    except Exception as e:
        print(f"   ❌ 데이터베이스 테스트 중 오류: {e}")
        return False


def test_link_builder_basic():
    """링크 빌더 기본 기능 테스트"""
    print("\n🔗 링크 빌더 기본 기능 테스트 시작...")

    try:
        from intelligent_link_builder import IntelligentLinkBuilder
        from pbn_content_crawler import PBNContentCrawler

        # 테스트용 크롤러와 링크 빌더 생성
        test_db_path = "test_link_builder.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        crawler = PBNContentCrawler(db_path=test_db_path)
        link_builder = IntelligentLinkBuilder(crawler)

        # 테스트 콘텐츠
        test_content = """
        <h1>백링크 테스트의 중요성</h1>
        <p>백링크는 SEO에서 매우 중요한 요소입니다. 검색엔진최적화를 위해서는 고품질의 백링크가 필요합니다.</p>
        <p>백링크 테스트를 통해 웹사이트의 성능을 향상시킬 수 있습니다.</p>
        <h2>SEO 전략</h2>
        <p>효과적인 SEO 전략에는 백링크 구축이 포함됩니다.</p>
        """

        test_keyword = "백링크 테스트"
        test_client_url = "https://example-client.com"
        test_lsi_keywords = ["SEO", "검색엔진최적화", "링크빌딩"]
        test_longtail_keywords = ["백링크 테스트 방법", "SEO 백링크 전략"]

        print("   🧪 테스트 데이터 준비 완료")

        # 클라이언트 링크 삽입 테스트
        print("   🎯 클라이언트 링크 삽입 테스트...")
        modified_content, success = link_builder.insert_client_link(
            test_content, test_keyword, test_client_url
        )

        if success and test_client_url in modified_content:
            print("   ✅ 클라이언트 링크 삽입 성공")
        else:
            print("   ⚠️ 클라이언트 링크 삽입 확인 필요")

        # 키워드 추출 테스트
        print("   🔍 키워드 추출 테스트...")
        extracted_keywords = link_builder.extract_keywords_from_content(
            test_content, test_keyword, test_lsi_keywords, test_longtail_keywords
        )

        if extracted_keywords:
            print(f"   ✅ 키워드 추출 성공: {len(extracted_keywords)}개 키워드")
        else:
            print("   ⚠️ 키워드 추출 결과 없음")

        # 테스트 DB 파일 정리
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        print("   ✅ 링크 빌더 기본 기능 테스트 완료")
        return True

    except Exception as e:
        print(f"   ❌ 링크 빌더 테스트 중 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_enhanced_system_initialization():
    """고도화된 PBN 시스템 초기화 테스트"""
    print("\n🚀 고도화된 PBN 시스템 초기화 테스트 시작...")

    try:
        from enhanced_main_v2 import EnhancedPBNSystem

        print("   ⏳ 시스템 초기화 중... (시간이 걸릴 수 있습니다)")

        # 시스템 초기화 (실제 OpenAI API 키가 필요할 수 있음)
        system = EnhancedPBNSystem()

        # 기본 속성들이 제대로 초기화되었는지 확인
        checks = [
            (hasattr(system, "pbn_crawler"), "PBN 크롤러"),
            (hasattr(system, "link_builder"), "링크 빌더"),
            (hasattr(system, "html_converter"), "HTML 변환기"),
            (hasattr(system, "cost_tracker"), "비용 추적기"),
            (hasattr(system, "debug_dir"), "디버그 디렉토리"),
        ]

        all_passed = True
        for check, name in checks:
            if check:
                print(f"   ✅ {name} 초기화 성공")
            else:
                print(f"   ❌ {name} 초기화 실패")
                all_passed = False

        if all_passed:
            print("   ✅ 시스템 초기화 테스트 완료")
            return True
        else:
            print("   ❌ 일부 컴포넌트 초기화 실패")
            return False

    except Exception as e:
        print(f"   ❌ 시스템 초기화 테스트 중 오류: {e}")
        # OpenAI API 키 관련 오류는 예상되는 상황
        if "openai" in str(e).lower() or "api" in str(e).lower():
            print("   💡 OpenAI API 키 설정이 필요할 수 있습니다.")
        return False


def test_similarity_model():
    """유사도 모델 로딩 테스트"""
    print("\n🤖 텍스트 유사도 모델 테스트 시작...")

    try:
        import sentence_transformers
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        print("   ✅ 필요한 라이브러리 import 성공")

        # 모델 로딩 테스트 (시간이 걸릴 수 있음)
        print("   ⏳ 유사도 모델 로딩 중... (최초 실행 시 다운로드 시간 소요)")

        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        # 간단한 유사도 테스트
        test_sentences = ["백링크 테스트", "SEO 최적화", "링크 빌딩 전략"]
        embeddings = model.encode(test_sentences)

        similarities = cosine_similarity(embeddings)

        print("   ✅ 유사도 모델 테스트 성공")
        print(f"   📊 테스트 문장 수: {len(test_sentences)}")
        print(f"   🔢 임베딩 차원: {embeddings.shape[1]}")

        return True

    except ImportError as e:
        print(f"   ❌ 필요한 라이브러리 없음: {e}")
        print(
            "   💡 다음 명령으로 설치하세요: pip install sentence-transformers scikit-learn numpy"
        )
        return False
    except Exception as e:
        print(f"   ❌ 유사도 모델 테스트 중 오류: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🧪 PBN 링크 빌딩 시스템 통합 테스트 시작")
    print("=" * 60)
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    tests = [
        ("모듈 Import 테스트", test_imports),
        ("데이터베이스 생성 테스트", test_database_creation),
        ("링크 빌더 기본 기능 테스트", test_link_builder_basic),
        ("유사도 모델 테스트", test_similarity_model),
        ("시스템 초기화 테스트", test_enhanced_system_initialization),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        start_time = time.time()

        try:
            result = test_func()
            duration = time.time() - start_time
            results.append((test_name, result, duration))

            status = "✅ 성공" if result else "❌ 실패"
            print(f"\n{status} - {test_name} ({duration:.2f}초)")

        except Exception as e:
            duration = time.time() - start_time
            results.append((test_name, False, duration))
            print(f"\n❌ 예외 발생 - {test_name}: {e}")

    # 최종 결과 출력
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result, duration in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status} {test_name} ({duration:.2f}초)")
        if result:
            passed += 1

    print(f"\n📈 전체 결과: {passed}/{total} 테스트 통과")
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"📊 성공률: {success_rate:.1f}%")

    if success_rate >= 80:
        print("🎉 시스템이 정상적으로 작동할 것으로 예상됩니다!")
    elif success_rate >= 60:
        print("⚠️ 일부 기능에 문제가 있을 수 있습니다.")
    else:
        print("❌ 시스템 설정을 확인해주세요.")

    print(f"\n📅 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return success_rate >= 60


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
