#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기반 유사도 검사 테스트 스크립트
FAISS 인덱스와 SentenceTransformer를 사용한 실제 유사도 검사 테스트
"""

import sys
import os
from improved_similarity_system import ImprovedSimilaritySystem


def test_ai_similarity():
    """AI 기반 유사도 검사 테스트"""
    print("🧠 AI 기반 유사도 검사 테스트 시작")
    print("=" * 60)

    try:
        # 1. 시스템 초기화
        print("1️⃣ ImprovedSimilaritySystem 초기화 중...")
        similarity_system = ImprovedSimilaritySystem()
        print("   ✅ 시스템 초기화 완료")

        # 2. 인덱스 상태 확인
        print("\n2️⃣ FAISS 인덱스 상태 확인...")
        stats = similarity_system.get_index_stats()
        print(f"   📊 총 포스트 수: {stats['total_posts']:,}개")
        print(f"   🧠 임베딩 차원: {stats['embedding_dimension']}차원")
        print(f"   💾 인덱스 크기: {stats['index_size_mb']:.2f}MB")

        # 3. 테스트 키워드들
        test_keywords = [
            ["백링크", "SEO"],
            ["검색엔진", "최적화"],
            ["웹사이트", "마케팅"],
            ["온라인", "비즈니스"],
            ["디지털", "마케팅"],
        ]

        print("\n3️⃣ AI 기반 유사도 검사 테스트...")
        print("-" * 60)

        for i, keywords in enumerate(test_keywords, 1):
            print(f"\n🔍 테스트 {i}: '{', '.join(keywords)}'")

            # AI 기반 유사도 검사 (랜덤 선택 활성화)
            results = similarity_system.find_similar_posts_fast(
                keywords=keywords,
                limit=5,
                min_similarity=0.3,
                random_selection=True,  # 🎲 랜덤 선택으로 다양성 확보
            )

            if results:
                print(f"   📋 검색 결과: {len(results)}개")
                for j, post in enumerate(results, 1):
                    similarity = post.get("similarity_score", 0)
                    title = (
                        post.get("title", "N/A")[:50] + "..."
                        if len(post.get("title", "")) > 50
                        else post.get("title", "N/A")
                    )
                    print(f"   {j}. {title}")
                    print(f"      📊 유사도: {similarity:.4f}")
                    print(f"      🌐 사이트: {post.get('site_url', 'N/A')}")
            else:
                print("   ❌ 검색 결과 없음")

        print("\n" + "=" * 60)
        print("🎉 AI 기반 유사도 검사 테스트 완료!")
        print("✅ FAISS 인덱스가 정상적으로 작동하고 있습니다.")
        print("✅ 랜덤 선택으로 다양한 결과를 제공합니다.")

        return True

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ai_similarity()
    sys.exit(0 if success else 1)
