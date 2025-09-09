#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_main_v2.py의 ImprovedSimilaritySystem 초기화 오류 디버깅
"""

import sys
import os
import traceback
from improved_similarity_system import ImprovedSimilaritySystem


def debug_enhanced_main_init():
    """enhanced_main_v2.py와 동일한 방식으로 초기화 테스트"""
    print("🔍 enhanced_main_v2.py 초기화 방식 디버깅")
    print("=" * 60)

    try:
        print("1️⃣ ImprovedSimilaritySystem 초기화 중...")
        print("   (enhanced_main_v2.py와 동일한 방식)")

        # enhanced_main_v2.py와 동일한 방식으로 초기화
        similarity_system = ImprovedSimilaritySystem()

        print("   ✅ 초기화 성공!")

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
            keywords=["웹사이트"], limit=3, min_similarity=0.3, random_selection=True
        )

        if test_results:
            print(f"   ✅ 검색 성공: {len(test_results)}개 결과")
            for i, result in enumerate(test_results, 1):
                print(f"   {i}. {result.get('title', 'N/A')[:50]}...")
                print(f"      📊 유사도: {result.get('similarity_score', 0):.3f}")
        else:
            print("   ❌ 검색 결과 없음")

        return True

    except Exception as e:
        print(f"\n❌ 초기화 중 오류 발생: {e}")
        print("\n🔍 상세 오류 정보:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = debug_enhanced_main_init()
    print(f"\n{'✅ 성공' if success else '❌ 실패'}")
    sys.exit(0 if success else 1)
