#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
콘텐츠 정리 및 워드프레스 호환성 테스트 스크립트
"""

import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_main_v2 import EnhancedPBNSystem
from wordpress_functions import WordPressManager
from controlDB import get_all_pbn_sites


def test_content_cleaning():
    """콘텐츠 정리 및 워드프레스 호환성 테스트"""
    print("🧪 콘텐츠 정리 테스트 시작")
    print("=" * 50)

    # 시스템 초기화
    system = EnhancedPBNSystem()

    # 테스트용 HTML 콘텐츠 (문제가 되는 요소들 포함)
    test_html = """
    <article class="fs-article">
    <nav class="fs-toc">
    <h2 id="toc-section" class="fs-h2">📚 목차</h2>
      <ol class="fs-toc-list">
        <li><a href="#핵심-용어-정리">핵심 용어 정리</a></li>
      </ol>
    </nav>
    
    <section class="fs-section">
    <h2 id="핵심-용어-정리" class="fs-h2">📖 핵심 용어 정리</h2>
    
    <p>본문을 읽기 전에 알아두면 좋은 용어들입니다.</p>
    
    <dl class="fs-terms">
      <dt class="fs-term-name">검색엔진 최적화</dt>
      <dd class="fs-term-description">웹사이트가 검색 결과에 잘 나오도록 하는 작업</dd>
    </dl>
    </section>
    
    <table class="fs-table">
      <thead>
        <tr>
          <th class="fs-table-header">항목</th>
          <th class="fs-table-header">설명</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="fs-table-cell">테스트</td>
          <td class="fs-table-cell">테스트 설명</td>
        </tr>
      </tbody>
    </table>
    </article>
    """

    print("🔧 원본 HTML 콘텐츠:")
    print(f"   크기: {len(test_html)} 바이트")
    print(f"   이모지 포함: {'📚' in test_html}")
    print(f"   커스텀 클래스 포함: {'fs-' in test_html}")

    # 콘텐츠 정리 테스트
    print("\n🧹 콘텐츠 정리 테스트...")
    cleaned_content = system._clean_content_for_wordpress(test_html)

    print(f"\n✅ 정리 후 콘텐츠:")
    print(f"   크기: {len(cleaned_content)} 바이트")
    print(f"   이모지 포함: {'📚' in cleaned_content}")
    print(f"   커스텀 클래스 포함: {'fs-' in cleaned_content}")

    # 정리된 콘텐츠 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/cleaned_test_content_{timestamp}.html"

    try:
        os.makedirs("data", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_content)
        print(f"📁 정리된 콘텐츠가 {output_file}에 저장되었습니다.")
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")

    # 간단한 HTML 생성 테스트
    print("\n🔧 간단한 HTML 생성 테스트...")

    test_content_data = {
        "title": "테스트 제목: 검색엔진 최적화 가이드",
        "content": """# 검색엔진 최적화 가이드

## 서론

검색엔진 최적화(SEO)는 **매우 중요한** 마케팅 전략입니다.

### 주요 포인트

- 키워드 분석
- 콘텐츠 최적화  
- 백링크 구축

자세한 내용은 [여기](https://example.com)에서 확인하세요.

## 결론

SEO는 *지속적인 노력*이 필요합니다.""",
    }

    try:
        simple_html = system._create_simple_html_content(test_content_data)

        print(f"✅ 간단한 HTML 생성 완료:")
        print(f"   크기: {len(simple_html)} 바이트")

        # 간단한 HTML 저장
        simple_output_file = f"data/simple_test_content_{timestamp}.html"
        with open(simple_output_file, "w", encoding="utf-8") as f:
            f.write(simple_html)
        print(f"📁 간단한 HTML이 {simple_output_file}에 저장되었습니다.")

    except Exception as e:
        print(f"❌ 간단한 HTML 생성 실패: {e}")
        import traceback

        traceback.print_exc()


def test_wordpress_upload_with_cleaned_content():
    """정리된 콘텐츠로 워드프레스 업로드 테스트"""
    print("\n" + "=" * 50)
    print("🔗 정리된 콘텐츠 워드프레스 업로드 테스트")
    print("=" * 50)

    # PBN 사이트 조회
    pbn_sites = get_all_pbn_sites()
    if not pbn_sites:
        print("❌ PBN 사이트가 없습니다.")
        return False

    pbn_site = pbn_sites[0]
    pbn_site_id, pbn_url, pbn_user, pbn_pass, pbn_app_pass = pbn_site

    if not pbn_app_pass:
        print("❌ 앱 패스워드가 없습니다.")
        return False

    # 간단한 테스트 콘텐츠
    simple_test_content = """
    <h1>SEO 테스트 포스트</h1>
    
    <h2>검색엔진 최적화란?</h2>
    <p>검색엔진 최적화(SEO)는 웹사이트가 검색 결과에서 더 잘 보이도록 하는 기법입니다.</p>
    
    <h3>주요 요소</h3>
    <p><strong>키워드</strong>: 사용자가 검색하는 단어들</p>
    <p><em>콘텐츠</em>: 유용하고 질 높은 정보</p>
    
    <h3>백링크의 중요성</h3>
    <p>다른 사이트에서 링크를 받는 것은 SEO에 매우 중요합니다.</p>
    
    <p>더 자세한 정보는 <a href="https://example.com">여기</a>를 참조하세요.</p>
    """

    try:
        wp_manager = WordPressManager()

        test_title = f"정리된 콘텐츠 테스트 {datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print("📤 정리된 콘텐츠로 테스트 포스트 업로드 중...")
        print(f"   콘텐츠 크기: {len(simple_test_content)} 바이트")

        result = wp_manager.create_post(
            site_url=pbn_url,
            username=pbn_user,
            app_password=pbn_app_pass,
            title=test_title,
            content=simple_test_content,
            status="draft",
        )

        if result:
            print(f"✅ 정리된 콘텐츠 업로드 성공!")
            print(f"📝 포스트 ID: {result}")
            print(f"🔗 포스트 URL: {pbn_url}/?p={result}")
            return True
        else:
            print("❌ 정리된 콘텐츠 업로드 실패")
            return False

    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 콘텐츠 정리 테스트
    test_content_cleaning()

    # 워드프레스 업로드 테스트
    test_wordpress_upload_with_cleaned_content()

    print("\n" + "=" * 50)
    print("🎉 모든 테스트 완료!")
