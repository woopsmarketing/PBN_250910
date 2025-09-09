#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_main_v2.py의 ImprovedSimilaritySystem 초기화 디버깅
"""

import sys
import os
from improved_similarity_system import ImprovedSimilaritySystem


def debug_similarity_system():
    """ImprovedSimilaritySystem 초기화 디버깅"""
    print("🔍 ImprovedSimilaritySystem 초기화 디버깅")
    print("=" * 50)

    try:
        print("1️⃣ ImprovedSimilaritySystem 인스턴스 생성 중...")
        similarity_system = ImprovedSimilaritySystem()
        print("   ✅ 인스턴스 생성 완료")

        print("\n2️⃣ 시스템 상태 확인...")
        print(
            f"   - similarity_model: {similarity_system.similarity_model is not None}"
        )
        print(f"   - faiss_index: {similarity_system.faiss_index is not None}")
        print(
            f"   - post_metadata: {len(similarity_system.post_metadata) if similarity_system.post_metadata else 0}개"
        )

        print("\n3️⃣ 간단한 검색 테스트...")
        test_results = similarity_system.find_similar_posts_fast(
            keywords=["SEO", "최적화"],
            limit=3,
            min_similarity=0.3,
            random_selection=True,
        )

        if test_results:
            print(f"   ✅ 검색 성공: {len(test_results)}개 결과")
            for i, result in enumerate(test_results, 1):
                print(
                    f"   {i}. {result.get('title', 'N/A')[:40]}... (유사도: {result.get('similarity_score', 0):.3f})"
                )
        else:
            print("   ❌ 검색 결과 없음")

        print("\n4️⃣ 통계 정보...")
        stats = similarity_system.get_index_stats()
        print(f"   - 총 포스트: {stats['total_posts']:,}개")
        print(f"   - 임베딩 차원: {stats['embedding_dimension']}차원")
        print(f"   - 인덱스 존재: {stats['index_exists']}")
        print(f"   - 모델 로드됨: {stats['model_loaded']}")

        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = debug_similarity_system()
    print(f"\n{'✅ 성공' if success else '❌ 실패'}")
    sys.exit(0 if success else 1)
