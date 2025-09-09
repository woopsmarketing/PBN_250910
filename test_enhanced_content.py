# v1.0 - 고도화된 콘텐츠 생성 테스트 스크립트
# 새로운 콘텐츠 생성 시스템의 기능을 테스트합니다.

import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_title_generator():
    """제목 생성기 테스트"""
    print("🧪 제목 생성기 테스트 시작")
    print("=" * 40)
    
    try:
        from src.generators.content.title_generator import AdvancedTitleGenerator, TitleConfig
        
        # 제목 생성기 설정
        config = TitleConfig(
            max_length=60,
            min_length=30,
            include_numbers=True,
            include_power_words=True,
            target_keyword="마케팅"
        )
        
        # 제목 생성기 인스턴스 생성
        generator = AdvancedTitleGenerator(config)
        
        # 제목 생성
        titles = generator.generate_titles(
            topic="성공하는 방법",
            target_keyword="마케팅",
            lsi_keywords=["디지털", "온라인", "전략"],
            num_titles=5
        )
        
        print("✅ 제목 생성 성공!")
        print(f"📊 생성된 제목 수: {len(titles)}")
        print("\n📝 생성된 제목들:")
        for i, title_info in enumerate(titles, 1):
            print(f"{i}. {title_info['title']}")
            print(f"   유형: {title_info['type']}")
            print(f"   길이: {title_info['length']}자")
            print(f"   SEO 점수: {title_info['seo_score']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 제목 생성기 테스트 실패: {e}")
        return False

def test_outline_generator():
    """목차 생성기 테스트"""
    print("🧪 목차 생성기 테스트 시작")
    print("=" * 40)
    
    try:
        from src.generators.content.outline_generator import AdvancedOutlineGenerator, OutlineConfig
        
        # 목차 생성기 설정
        config = OutlineConfig(
            min_sections=7,
            max_sections=10,
            include_faq=True,
            include_tips=True,
            target_word_count=2000
        )
        
        # 목차 생성기 인스턴스 생성
        generator = AdvancedOutlineGenerator(config)
        
        # 목차 생성
        outline = generator.generate_outline(
            topic="성공하는 방법",
            target_keyword="마케팅",
            lsi_keywords=["디지털", "온라인", "전략"],
            content_type="guide"
        )
        
        print("✅ 목차 생성 성공!")
        print(f"📊 총 섹션 수: {outline['total_sections']}")
        print(f"📝 예상 단어 수: {outline['estimated_word_count']}")
        print(f"🎯 SEO 점수: {outline['seo_score']}")
        print("\n📋 생성된 섹션들:")
        for i, section in enumerate(outline['sections'], 1):
            print(f"{i}. {section.title}")
            print(f"   앵커: #{section.anchor}")
            print(f"   유형: {section.section_type.value}")
            print(f"   예상 단어 수: {section.word_count}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 목차 생성기 테스트 실패: {e}")
        return False

def test_section_generator():
    """섹션 생성기 테스트"""
    print("🧪 섹션 생성기 테스트 시작")
    print("=" * 40)
    
    try:
        from src.generators.content.section_generator import AdvancedSectionGenerator, SectionConfig, ContentTone
        
        # 섹션 생성기 설정
        config = SectionConfig(
            min_words=200,
            max_words=500,
            include_subheadings=True,
            include_bullet_points=True,
            include_examples=True,
            include_statistics=True,
            tone=ContentTone.PROFESSIONAL
        )
        
        # 섹션 생성기 인스턴스 생성
        generator = AdvancedSectionGenerator(config)
        
        # 섹션 콘텐츠 생성
        result = generator.generate_section_content(
            section_title="마케팅의 핵심 원리",
            topic="성공하는 방법",
            target_keyword="마케팅",
            lsi_keywords=["디지털", "온라인", "전략"],
            section_type="main_content"
        )
        
        print("✅ 섹션 생성 성공!")
        print(f"📊 단어 수: {result['word_count']}")
        print(f"🎯 SEO 점수: {result['seo_score']}")
        print(f"🏗️ 구조: {result['structure']}")
        print("\n📝 생성된 콘텐츠 (처음 300자):")
        print(result['content'][:300] + "...")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 섹션 생성기 테스트 실패: {e}")
        return False

def test_keyword_generator():
    """키워드 생성기 테스트"""
    print("🧪 키워드 생성기 테스트 시작")
    print("=" * 40)
    
    try:
        from src.generators.content.keyword_generator import AdvancedKeywordGenerator, KeywordConfig
        
        # 키워드 생성기 설정
        config = KeywordConfig(
            min_terms=5,
            max_terms=8,
            include_examples=True,
            include_related_terms=True
        )
        
        # 키워드 생성기 인스턴스 생성
        generator = AdvancedKeywordGenerator(config)
        
        # 용어 정의 생성
        result = generator.generate_keyword_definitions(
            topic="성공하는 방법",
            target_keyword="마케팅",
            lsi_keywords=["디지털", "온라인", "전략"],
            content_type="guide"
        )
        
        print("✅ 키워드 생성 성공!")
        print(f"📊 총 용어 수: {result['total_terms']}")
        print(f"🎯 SEO 점수: {result['seo_score']}")
        print("\n🔑 생성된 용어들:")
        for i, term_def in enumerate(result['terms'], 1):
            print(f"{i}. {term_def.term}")
            print(f"   정의: {term_def.definition}")
            print(f"   중요도: {term_def.importance}/5")
            if term_def.examples:
                print(f"   예시: {', '.join(term_def.examples)}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 키워드 생성기 테스트 실패: {e}")
        return False

def test_image_generator():
    """이미지 생성기 테스트"""
    print("🧪 이미지 생성기 테스트 시작")
    print("=" * 40)
    
    try:
        from src.generators.content.image_generator import AdvancedImageGenerator, ImageConfig, ImageStyle, ImageType
        
        # 이미지 생성기 설정
        config = ImageConfig(
            include_alt_text=True,
            include_caption=True,
            include_meta_description=True,
            max_alt_length=125,
            max_caption_length=200,
            style=ImageStyle.PROFESSIONAL
        )
        
        # 이미지 생성기 인스턴스 생성
        generator = AdvancedImageGenerator(config)
        
        # 이미지 메타데이터 생성
        metadata = generator.generate_image_metadata(
            topic="성공하는 방법",
            target_keyword="마케팅",
            lsi_keywords=["디지털", "온라인", "전략"],
            image_type=ImageType.FEATURED
        )
        
        print("✅ 이미지 생성 성공!")
        print(f"📊 제목: {metadata['title']}")
        print(f"📝 Alt 텍스트: {metadata['alt_text']}")
        print(f"📋 캡션: {metadata['caption']}")
        print(f"🎯 SEO 점수: {metadata['seo_score']}")
        print(f"📐 권장 크기: {metadata['recommended_size']}")
        print(f"🎨 색상 팔레트: {metadata['color_scheme']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 이미지 생성기 테스트 실패: {e}")
        return False

def test_integrated_content_generator():
    """통합 콘텐츠 생성기 테스트"""
    print("🧪 통합 콘텐츠 생성기 테스트 시작")
    print("=" * 40)
    
    try:
        from src.generators.content.advanced_content_generator import AdvancedContentGenerator, ContentConfig
        
        # 통합 콘텐츠 생성기 설정
        config = ContentConfig(
            target_word_count=2000,
            min_word_count=1500,
            max_word_count=3000,
            include_toc=True,
            include_keyword_definitions=True,
            include_images=True,
            num_images=3
        )
        
        # 통합 콘텐츠 생성기 인스턴스 생성
        generator = AdvancedContentGenerator(config)
        
        # 완전한 콘텐츠 생성
        content = generator.generate_complete_content(
            topic="성공하는 방법",
            target_keyword="마케팅",
            lsi_keywords=["디지털", "온라인", "전략"],
            content_type="guide"
        )
        
        print("✅ 통합 콘텐츠 생성 성공!")
        print(f"📊 제목: {content['title']}")
        print(f"📝 총 단어 수: {content['statistics']['total_word_count']}")
        print(f"📋 총 섹션 수: {content['statistics']['total_sections']}")
        print(f"🎯 SEO 점수: {content['statistics']['seo_score']}")
        print(f"🖼️ 이미지 수: {len(content.get('images', []))}")
        print(f"🔑 용어 정의 수: {len(content.get('keyword_definitions', {}).get('terms', []))}")
        print("\n📝 생성된 콘텐츠 (처음 500자):")
        print(content['content'][:500] + "...")
        print()
        
        # 워드프레스 포맷으로 내보내기
        wp_format = generator.export_to_wordpress_format(content)
        print("📤 워드프레스 포맷 내보내기 성공!")
        print(f"   포스트 제목: {wp_format['post_title']}")
        print(f"   포스트 상태: {wp_format['post_status']}")
        print(f"   포커스 키워드: {wp_format['meta']['focus_keyword']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 통합 콘텐츠 생성기 테스트 실패: {e}")
        return False

def run_all_tests():
    """모든 테스트를 실행합니다."""
    print("🚀 고도화된 콘텐츠 생성 시스템 테스트 시작")
    print("=" * 60)
    print(f"⏰ 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("제목 생성기", test_title_generator),
        ("목차 생성기", test_outline_generator),
        ("섹션 생성기", test_section_generator),
        ("키워드 생성기", test_keyword_generator),
        ("이미지 생성기", test_image_generator),
        ("통합 콘텐츠 생성기", test_integrated_content_generator)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 최종 결과 출력
    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료!")
    print(f"⏰ 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📊 테스트 결과 요약:")
    successful_tests = 0
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {test_name}: {status}")
        if success:
            successful_tests += 1
    
    print(f"\n📈 전체 성공률: {successful_tests}/{len(results)} ({successful_tests/len(results)*100:.1f}%)")
    
    if successful_tests == len(results):
        print("🎊 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 오류를 확인해주세요.")

if __name__ == "__main__":
    run_all_tests()