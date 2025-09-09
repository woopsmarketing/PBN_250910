#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAISS 인덱스 구축 스크립트
18,882개 PBN 포스트의 제목을 임베딩하여 FAISS 인덱스 생성
"""

import sys
import os
import time
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from improved_similarity_system import ImprovedSimilaritySystem


def build_faiss_index():
    """FAISS 인덱스 구축"""

    print("🏗️ FAISS 인덱스 구축 시작")
    print("=" * 50)

    start_time = time.time()

    try:
        # 시스템 초기화
        print("🔧 시스템 초기화 중...")
        similarity_system = ImprovedSimilaritySystem()

        # 데이터베이스에서 포스트 수 확인
        print("📊 데이터베이스 상태 확인 중...")
        posts = similarity_system._get_all_posts_from_db()

        if not posts:
            print("❌ 데이터베이스에 포스트가 없습니다.")
            print("   먼저 PBN 크롤링을 실행해주세요.")
            return False

        print(f"✅ {len(posts):,}개 포스트 발견")

        # FAISS 인덱스 구축
        print("\n🔨 FAISS 인덱스 구축 중...")
        print("   이 과정은 시간이 걸릴 수 있습니다...")

        # 인덱스 재구성 (새로 생성)
        similarity_system._rebuild_index()

        # 구축 완료 확인
        if similarity_system.faiss_index and similarity_system.post_metadata:
            print(f"✅ FAISS 인덱스 구축 완료!")
            print(f"   📄 포스트 수: {len(similarity_system.post_metadata):,}개")
            print(f"   🔍 인덱스 크기: {similarity_system.faiss_index.ntotal:,}개 벡터")

            # 인덱스 저장
            print("\n💾 인덱스 저장 중...")
            similarity_system._save_index()

            elapsed_time = time.time() - start_time
            print(f"⏱️ 총 소요 시간: {elapsed_time:.1f}초")

            return True
        else:
            print("❌ FAISS 인덱스 구축 실패")
            return False

    except Exception as e:
        print(f"❌ FAISS 인덱스 구축 중 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_faiss_index():
    """구축된 FAISS 인덱스 테스트"""

    print("\n🧪 FAISS 인덱스 테스트")
    print("=" * 30)

    try:
        # 시스템 초기화
        similarity_system = ImprovedSimilaritySystem()

        # 테스트 키워드들
        test_keywords = [["백링크"], ["SEO"], ["검색엔진"], ["마케팅"], ["웹사이트"]]

        for keywords in test_keywords:
            print(f"\n🔍 테스트 키워드: {keywords}")

            # 유사도 검색 테스트
            results = similarity_system.find_similar_posts_fast(
                keywords, limit=3, min_similarity=0.3, random_selection=True
            )

            if results:
                print(f"   ✅ {len(results)}개 결과 발견:")
                for i, result in enumerate(results):
                    print(
                        f"      {i+1}. {result['title'][:40]}... (유사도: {result['similarity_score']:.3f})"
                    )
            else:
                print("   ❌ 결과 없음")

        print("\n🎉 FAISS 인덱스 테스트 완료!")
        return True

    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        return False


def main():
    """메인 실행 함수"""

    print("🚀 PBN FAISS 인덱스 구축 시스템")
    print("=" * 50)

    # 1단계: FAISS 인덱스 구축
    print("\n📋 1단계: FAISS 인덱스 구축")
    if not build_faiss_index():
        print("❌ FAISS 인덱스 구축 실패")
        return

    # 2단계: 인덱스 테스트
    print("\n📋 2단계: 인덱스 테스트")
    if not test_faiss_index():
        print("❌ FAISS 인덱스 테스트 실패")
        return

    print("\n🎉 모든 과정이 완료되었습니다!")
    print("\n📋 다음 단계:")
    print("1. python enhanced_main_v2.py 실행")
    print("2. 메뉴에서 '23. 키워드 기반 유사 포스트 검색 테스트' 선택")
    print("3. 실제 링크 빌딩 시스템 사용")


if __name__ == "__main__":
    main()
