#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_main_v2.py와 동일한 환경에서 ImprovedSimilaritySystem 테스트
"""

import sys
import os
import traceback

# enhanced_main_v2.py와 동일한 import들
from controlDB import ControlDB
from wordpress_functions import WordPressManager
from src.generators.html.simple_html_converter import SimpleHTMLConverter
from pbn_content_crawler import PBNContentCrawler
from intelligent_link_builder import IntelligentLinkBuilder
from improved_similarity_system import ImprovedSimilaritySystem


def test_enhanced_main_environment():
    """enhanced_main_v2.py와 동일한 환경에서 테스트"""
    print("🔍 enhanced_main_v2.py 환경에서 ImprovedSimilaritySystem 테스트")
    print("=" * 70)

    try:
        # 1. 기본 시스템 초기화 (enhanced_main_v2.py와 동일)
        print("1️⃣ 기본 시스템 초기화...")
        db = ControlDB()
        wp_manager = WordPressManager()
        html_converter = SimpleHTMLConverter()
        pbn_crawler = PBNContentCrawler()
        print("   ✅ 기본 시스템 초기화 완료")

        # 2. ImprovedSimilaritySystem 초기화
        print("\n2️⃣ ImprovedSimilaritySystem 초기화...")
        similarity_system = ImprovedSimilaritySystem()
        print("   ✅ ImprovedSimilaritySystem 초기화 완료")

        # 3. 상태 확인
        print("\n3️⃣ 상태 확인...")
        print(f"   - faiss_index: {similarity_system.faiss_index is not None}")
        print(
            f"   - similarity_model: {similarity_system.similarity_model is not None}"
        )
        print(
            f"   - post_metadata: {len(similarity_system.post_metadata) if similarity_system.post_metadata else 0}개"
        )

        # 4. 간단한 검색 테스트
        print("\n4️⃣ 검색 테스트...")
        results = similarity_system.find_similar_posts_fast(
            keywords=["웹사이트", "백링크"],
            limit=3,
            min_similarity=0.3,
            random_selection=True,
        )

        if results:
            print(f"   ✅ 검색 성공: {len(results)}개 결과")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.get('title', 'N/A')[:50]}...")
                print(f"      📊 유사도: {result.get('similarity_score', 0):.3f}")
        else:
            print("   ❌ 검색 결과 없음")

        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n🔍 상세 오류 정보:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_enhanced_main_environment()
    print(f"\n{'✅ 성공' if success else '❌ 실패'}")
    sys.exit(0 if success else 1)
