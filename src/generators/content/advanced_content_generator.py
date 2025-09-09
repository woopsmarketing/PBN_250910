# v1.0 - 통합 고도화 콘텐츠 생성기 (PBN 시스템용)
# 모든 콘텐츠 요소를 통합하여 고품질 블로그 포스트 생성

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json

# 내부 모듈 import
from .title_generator import AdvancedTitleGenerator, TitleConfig, TitleType
from .outline_generator import AdvancedOutlineGenerator, OutlineConfig, SectionType
from .section_generator import AdvancedSectionGenerator, SectionConfig, ContentTone
from .keyword_generator import AdvancedKeywordGenerator, KeywordConfig, TermType
from .image_generator import AdvancedImageGenerator, ImageConfig, ImageType

@dataclass
class ContentConfig:
    """통합 콘텐츠 생성 설정"""
    # 제목 설정
    title_config: TitleConfig = None
    
    # 목차 설정
    outline_config: OutlineConfig = None
    
    # 섹션 설정
    section_config: SectionConfig = None
    
    # 키워드 설정
    keyword_config: KeywordConfig = None
    
    # 이미지 설정
    image_config: ImageConfig = None
    
    # 전체 설정
    target_word_count: int = 2000
    min_word_count: int = 1500
    max_word_count: int = 3000
    include_toc: bool = True
    include_keyword_definitions: bool = True
    include_images: bool = True
    num_images: int = 3

class AdvancedContentGenerator:
    """통합 고도화 콘텐츠 생성기"""
    
    def __init__(self, config: ContentConfig = None):
        self.config = config or ContentConfig()
        
        # 각 생성기 초기화
        self.title_generator = AdvancedTitleGenerator(self.config.title_config)
        self.outline_generator = AdvancedOutlineGenerator(self.config.outline_config)
        self.section_generator = AdvancedSectionGenerator(self.config.section_config)
        self.keyword_generator = AdvancedKeywordGenerator(self.config.keyword_config)
        self.image_generator = AdvancedImageGenerator(self.config.image_config)
    
    def generate_complete_content(self, 
                                 topic: str,
                                 target_keyword: str,
                                 lsi_keywords: List[str] = None,
                                 content_type: str = "guide",
                                 client_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        완전한 고품질 콘텐츠를 생성합니다.
        
        Args:
            topic: 주제
            target_keyword: 타겟 키워드
            lsi_keywords: LSI 키워드 목록
            content_type: 콘텐츠 유형
            client_info: 클라이언트 정보
            
        Returns:
            완전한 콘텐츠 정보 딕셔너리
        """
        # 1. 제목 생성
        print("📝 제목 생성 중...")
        titles = self.title_generator.generate_titles(
            topic=topic,
            target_keyword=target_keyword,
            lsi_keywords=lsi_keywords,
            num_titles=5
        )
        best_title = titles[0] if titles else {"title": f"{target_keyword} {topic} 가이드"}
        
        # 2. 목차 생성
        print("📋 목차 생성 중...")
        outline = self.outline_generator.generate_outline(
            topic=topic,
            target_keyword=target_keyword,
            lsi_keywords=lsi_keywords,
            content_type=content_type
        )
        
        # 3. 섹션별 콘텐츠 생성
        print("📄 섹션 콘텐츠 생성 중...")
        section_contents = []
        total_word_count = 0
        
        for section in outline['sections']:
            section_content = self.section_generator.generate_section_content(
                section_title=section.title,
                topic=topic,
                target_keyword=target_keyword,
                lsi_keywords=lsi_keywords,
                section_type=section.section_type.value
            )
            section_contents.append(section_content)
            total_word_count += section_content['word_count']
        
        # 4. 키워드 정의 생성
        print("🔑 키워드 정의 생성 중...")
        keyword_definitions = None
        if self.config.include_keyword_definitions:
            keyword_definitions = self.keyword_generator.generate_keyword_definitions(
                topic=topic,
                target_keyword=target_keyword,
                lsi_keywords=lsi_keywords,
                content_type=content_type
            )
        
        # 5. 이미지 메타데이터 생성
        print("🖼️ 이미지 메타데이터 생성 중...")
        images = None
        if self.config.include_images:
            images = self.image_generator.generate_multiple_images(
                topic=topic,
                target_keyword=target_keyword,
                lsi_keywords=lsi_keywords,
                num_images=self.config.num_images
            )
        
        # 6. 전체 콘텐츠 조합
        print("🔗 전체 콘텐츠 조합 중...")
        full_content = self._combine_full_content(
            best_title['title'],
            outline,
            section_contents,
            keyword_definitions,
            images
        )
        
        # 7. SEO 점수 계산
        seo_score = self._calculate_overall_seo_score(
            best_title, outline, section_contents, keyword_definitions, images
        )
        
        # 8. 메타데이터 생성
        meta_data = self._generate_meta_data(
            topic, target_keyword, lsi_keywords, content_type, client_info
        )
        
        return {
            "title": best_title['title'],
            "content": full_content,
            "outline": outline,
            "sections": section_contents,
            "keyword_definitions": keyword_definitions,
            "images": images,
            "meta_data": meta_data,
            "statistics": {
                "total_word_count": total_word_count,
                "total_sections": len(section_contents),
                "seo_score": seo_score,
                "generated_at": datetime.now().isoformat(),
                "content_type": content_type
            }
        }
    
    def _combine_full_content(self, 
                             title: str,
                             outline: Dict[str, Any],
                             section_contents: List[Dict[str, Any]],
                             keyword_definitions: Optional[Dict[str, Any]],
                             images: Optional[List[Dict[str, Any]]]) -> str:
        """전체 콘텐츠를 조합합니다."""
        content = f"# {title}\n\n"
        
        # 목차 추가
        if self.config.include_toc and outline.get('toc_html'):
            content += outline['toc_html'] + "\n\n"
        
        # 섹션별 콘텐츠 추가
        for i, section_content in enumerate(section_contents):
            content += f"## {outline['sections'][i].title}\n\n"
            content += section_content['content'] + "\n\n"
            
            # 이미지 추가 (해당 섹션에 맞는 이미지)
            if images and i < len(images):
                img = images[i]
                content += f"![{img['alt_text']}]({img['filename']})\n"
                content += f"*{img['caption']}*\n\n"
        
        # 키워드 정의 추가
        if keyword_definitions and self.config.include_keyword_definitions:
            content += keyword_definitions['html_content'] + "\n\n"
        
        # 마무리
        content += "---\n\n"
        content += f"*이 글은 {title}에 대한 종합적인 가이드입니다. "
        content += "더 자세한 정보가 필요하시면 언제든지 문의해 주세요.*\n"
        
        return content
    
    def _calculate_overall_seo_score(self, 
                                   title: Dict[str, Any],
                                   outline: Dict[str, Any],
                                   section_contents: List[Dict[str, Any]],
                                   keyword_definitions: Optional[Dict[str, Any]],
                                   images: Optional[List[Dict[str, Any]]]) -> int:
        """전체 SEO 점수를 계산합니다."""
        total_score = 0
        
        # 제목 점수
        total_score += title.get('seo_score', 0)
        
        # 목차 점수
        total_score += outline.get('seo_score', 0)
        
        # 섹션 콘텐츠 점수
        for section_content in section_contents:
            total_score += section_content.get('seo_score', 0)
        
        # 키워드 정의 점수
        if keyword_definitions:
            total_score += keyword_definitions.get('seo_score', 0)
        
        # 이미지 점수
        if images:
            for image in images:
                total_score += image.get('seo_score', 0)
        
        return total_score
    
    def _generate_meta_data(self, 
                           topic: str,
                           target_keyword: str,
                           lsi_keywords: List[str],
                           content_type: str,
                           client_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """메타데이터를 생성합니다."""
        meta_data = {
            "topic": topic,
            "target_keyword": target_keyword,
            "lsi_keywords": lsi_keywords or [],
            "content_type": content_type,
            "generated_at": datetime.now().isoformat(),
            "seo_optimized": True,
            "content_quality": "high"
        }
        
        if client_info:
            meta_data.update({
                "client_id": client_info.get('id'),
                "client_name": client_info.get('name'),
                "target_url": client_info.get('target_url'),
                "pbn_site": client_info.get('pbn_site')
            })
        
        return meta_data
    
    def generate_content_for_pbn(self, 
                                pbn_site: Dict[str, Any],
                                client: Dict[str, Any],
                                keyword: str) -> Dict[str, Any]:
        """PBN 사이트용 콘텐츠를 생성합니다."""
        
        # 클라이언트 정보에서 주제 추출
        topic = client.get('topic', keyword)
        lsi_keywords = client.get('lsi_keywords', [])
        content_type = client.get('content_type', 'guide')
        
        # 콘텐츠 생성
        content = self.generate_complete_content(
            topic=topic,
            target_keyword=keyword,
            lsi_keywords=lsi_keywords,
            content_type=content_type,
            client_info={
                'id': client.get('id'),
                'name': client.get('name'),
                'target_url': client.get('target_url'),
                'pbn_site': pbn_site.get('url')
            }
        )
        
        # PBN 사이트별 맞춤화
        content['pbn_optimized'] = self._optimize_for_pbn(content, pbn_site)
        
        return content
    
    def _optimize_for_pbn(self, content: Dict[str, Any], pbn_site: Dict[str, Any]) -> Dict[str, Any]:
        """PBN 사이트에 맞게 콘텐츠를 최적화합니다."""
        return {
            "site_url": pbn_site.get('url'),
            "site_theme": pbn_site.get('theme', 'general'),
            "target_audience": pbn_site.get('audience', 'general'),
            "content_style": pbn_site.get('style', 'professional'),
            "optimization_level": "high"
        }
    
    def save_content_to_file(self, 
                            content: Dict[str, Any], 
                            filename: str = None) -> str:
        """콘텐츠를 파일로 저장합니다."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_{timestamp}.json"
        
        # 콘텐츠를 JSON으로 저장
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def export_to_wordpress_format(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """워드프레스 포맷으로 내보냅니다."""
        return {
            "post_title": content['title'],
            "post_content": content['content'],
            "post_status": "publish",
            "post_type": "post",
            "meta": {
                "seo_title": content['title'],
                "seo_description": content['meta_data'].get('description', ''),
                "focus_keyword": content['meta_data']['target_keyword'],
                "lsi_keywords": content['meta_data']['lsi_keywords']
            },
            "images": content.get('images', []),
            "statistics": content['statistics']
        }

# 사용 예시
if __name__ == "__main__":
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
    
    # 결과 출력
    print("=== 생성된 콘텐츠 ===")
    print(f"제목: {content['title']}")
    print(f"총 단어 수: {content['statistics']['total_word_count']}")
    print(f"총 섹션 수: {content['statistics']['total_sections']}")
    print(f"SEO 점수: {content['statistics']['seo_score']}")
    print()
    
    print("=== 콘텐츠 미리보기 ===")
    print(content['content'][:500] + "...")
    print()
    
    # 워드프레스 포맷으로 내보내기
    wp_format = generator.export_to_wordpress_format(content)
    print("=== 워드프레스 포맷 ===")
    print(f"포스트 제목: {wp_format['post_title']}")
    print(f"포스트 상태: {wp_format['post_status']}")
    print(f"포커스 키워드: {wp_format['meta']['focus_keyword']}")
    print(f"이미지 수: {len(wp_format['images'])}")