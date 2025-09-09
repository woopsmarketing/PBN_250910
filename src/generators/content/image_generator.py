# v1.0 - 고도화된 이미지 생성기 (PBN 시스템용)
# SEO 최적화된 이미지 메타데이터 및 설명 생성

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import random

class ImageType(Enum):
    """이미지 유형 정의"""
    FEATURED = "featured"
    INFOGRAPHIC = "infographic"
    CHART = "chart"
    DIAGRAM = "diagram"
    SCREENSHOT = "screenshot"
    ILLUSTRATION = "illustration"

class ImageStyle(Enum):
    """이미지 스타일 정의"""
    PROFESSIONAL = "professional"
    MODERN = "modern"
    MINIMALIST = "minimalist"
    COLORFUL = "colorful"
    MONOCHROME = "monochrome"

@dataclass
class ImageConfig:
    """이미지 생성 설정"""
    include_alt_text: bool = True
    include_caption: bool = True
    include_meta_description: bool = True
    max_alt_length: int = 125
    max_caption_length: int = 200
    style: ImageStyle = ImageStyle.PROFESSIONAL

class AdvancedImageGenerator:
    """고도화된 이미지 생성기"""
    
    def __init__(self, config: ImageConfig = None):
        self.config = config or ImageConfig()
        self.image_templates = {
            ImageType.FEATURED: [
                "{keyword} {topic} 완벽 가이드",
                "{keyword} {topic} 전문가 조언",
                "{keyword} {topic} 성공 비법"
            ],
            ImageType.INFOGRAPHIC: [
                "{keyword} {topic} 핵심 포인트",
                "{keyword} {topic} 단계별 가이드",
                "{keyword} {topic} 통계 자료"
            ],
            ImageType.CHART: [
                "{keyword} {topic} 성과 분석",
                "{keyword} {topic} 비교 차트",
                "{keyword} {topic} 트렌드 분석"
            ],
            ImageType.DIAGRAM: [
                "{keyword} {topic} 프로세스",
                "{keyword} {topic} 구조도",
                "{keyword} {topic} 워크플로우"
            ],
            ImageType.SCREENSHOT: [
                "{keyword} {topic} 실제 화면",
                "{keyword} {topic} 사용 예시",
                "{keyword} {topic} 결과 화면"
            ],
            ImageType.ILLUSTRATION: [
                "{keyword} {topic} 개념도",
                "{keyword} {topic} 시각적 설명",
                "{keyword} {topic} 아이디어 스케치"
            ]
        }
        
        self.alt_text_templates = [
            "{keyword} {topic}에 대한 {image_type} 이미지",
            "{keyword} {topic}를 보여주는 {image_type}",
            "{keyword} {topic} 관련 {image_type} 자료",
            "{keyword} {topic}의 핵심을 담은 {image_type}"
        ]
        
        self.caption_templates = [
            "이 {image_type}는 {keyword} {topic}의 핵심 내용을 시각적으로 보여줍니다.",
            "{keyword} {topic}에 대한 이해를 돕는 {image_type}입니다.",
            "위 {image_type}는 {keyword} {topic}의 주요 포인트를 요약한 것입니다.",
            "{keyword} {topic}의 성공을 위한 {image_type} 가이드입니다."
        ]
    
    def generate_image_metadata(self, 
                               topic: str,
                               target_keyword: str,
                               lsi_keywords: List[str] = None,
                               image_type: ImageType = ImageType.FEATURED,
                               section_title: str = "") -> Dict[str, any]:
        """
        이미지 메타데이터를 생성합니다.
        
        Args:
            topic: 주제
            target_keyword: 타겟 키워드
            lsi_keywords: LSI 키워드 목록
            image_type: 이미지 유형
            section_title: 섹션 제목
            
        Returns:
            이미지 메타데이터 딕셔너리
        """
        # 이미지 제목 생성
        title = self._generate_image_title(topic, target_keyword, lsi_keywords, image_type)
        
        # Alt 텍스트 생성
        alt_text = self._generate_alt_text(topic, target_keyword, lsi_keywords, image_type)
        
        # 캡션 생성
        caption = self._generate_caption(topic, target_keyword, lsi_keywords, image_type)
        
        # 메타 설명 생성
        meta_description = self._generate_meta_description(topic, target_keyword, lsi_keywords, image_type)
        
        # 파일명 생성
        filename = self._generate_filename(topic, target_keyword, image_type)
        
        # SEO 점수 계산
        seo_score = self._calculate_seo_score(title, alt_text, caption, target_keyword, lsi_keywords)
        
        return {
            "title": title,
            "alt_text": alt_text,
            "caption": caption,
            "meta_description": meta_description,
            "filename": filename,
            "image_type": image_type.value,
            "seo_score": seo_score,
            "recommended_size": self._get_recommended_size(image_type),
            "color_scheme": self._get_color_scheme(image_type),
            "style_guide": self._get_style_guide(image_type)
        }
    
    def _generate_image_title(self, 
                             topic: str,
                             target_keyword: str,
                             lsi_keywords: List[str],
                             image_type: ImageType) -> str:
        """이미지 제목을 생성합니다."""
        templates = self.image_templates.get(image_type, [])
        
        if not templates:
            return f"{target_keyword} {topic} 이미지"
        
        # LSI 키워드가 있으면 활용
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            template = templates[0].replace("{keyword}", f"{target_keyword} {lsi}")
        else:
            template = templates[0].replace("{keyword}", target_keyword)
        
        return template.replace("{topic}", topic)
    
    def _generate_alt_text(self, 
                          topic: str,
                          target_keyword: str,
                          lsi_keywords: List[str],
                          image_type: ImageType) -> str:
        """Alt 텍스트를 생성합니다."""
        if not self.config.include_alt_text:
            return ""
        
        templates = self.alt_text_templates
        template = random.choice(templates)
        
        # LSI 키워드가 있으면 활용
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            keyword = f"{target_keyword} {lsi}"
        else:
            keyword = target_keyword
        
        alt_text = template.replace("{keyword}", keyword)
        alt_text = alt_text.replace("{topic}", topic)
        alt_text = alt_text.replace("{image_type}", image_type.value)
        
        # 길이 제한
        if len(alt_text) > self.config.max_alt_length:
            alt_text = alt_text[:self.config.max_alt_length-3] + "..."
        
        return alt_text
    
    def _generate_caption(self, 
                         topic: str,
                         target_keyword: str,
                         lsi_keywords: List[str],
                         image_type: ImageType) -> str:
        """캡션을 생성합니다."""
        if not self.config.include_caption:
            return ""
        
        templates = self.caption_templates
        template = random.choice(templates)
        
        # LSI 키워드가 있으면 활용
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            keyword = f"{target_keyword} {lsi}"
        else:
            keyword = target_keyword
        
        caption = template.replace("{keyword}", keyword)
        caption = caption.replace("{topic}", topic)
        caption = caption.replace("{image_type}", image_type.value)
        
        # 길이 제한
        if len(caption) > self.config.max_caption_length:
            caption = caption[:self.config.max_caption_length-3] + "..."
        
        return caption
    
    def _generate_meta_description(self, 
                                  topic: str,
                                  target_keyword: str,
                                  lsi_keywords: List[str],
                                  image_type: ImageType) -> str:
        """메타 설명을 생성합니다."""
        if not self.config.include_meta_description:
            return ""
        
        # LSI 키워드가 있으면 활용
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            keyword = f"{target_keyword} {lsi}"
        else:
            keyword = target_keyword
        
        meta_description = f"{keyword} {topic}에 대한 {image_type.value} 이미지입니다. "
        meta_description += f"이 이미지는 {topic}의 핵심 내용을 시각적으로 보여주며, "
        meta_description += f"{target_keyword}의 이해를 돕습니다."
        
        return meta_description
    
    def _generate_filename(self, 
                          topic: str,
                          target_keyword: str,
                          image_type: ImageType) -> str:
        """파일명을 생성합니다."""
        # 한글을 영문으로 변환 (간단한 매핑)
        korean_to_english = {
            "마케팅": "marketing",
            "비즈니스": "business",
            "성공": "success",
            "방법": "method",
            "가이드": "guide",
            "전략": "strategy",
            "기법": "technique",
            "도구": "tool",
            "원리": "principle"
        }
        
        # 주제와 키워드를 영문으로 변환
        topic_en = korean_to_english.get(topic, topic.lower())
        keyword_en = korean_to_english.get(target_keyword, target_keyword.lower())
        
        # 파일명 생성
        filename = f"{keyword_en}_{topic_en}_{image_type.value}"
        
        # 특수문자 제거
        filename = re.sub(r'[^\w\-_]', '', filename)
        
        return filename
    
    def _get_recommended_size(self, image_type: ImageType) -> Dict[str, int]:
        """이미지 유형별 권장 크기를 반환합니다."""
        size_mapping = {
            ImageType.FEATURED: {"width": 1200, "height": 630},
            ImageType.INFOGRAPHIC: {"width": 800, "height": 1200},
            ImageType.CHART: {"width": 800, "height": 600},
            ImageType.DIAGRAM: {"width": 800, "height": 600},
            ImageType.SCREENSHOT: {"width": 800, "height": 600},
            ImageType.ILLUSTRATION: {"width": 600, "height": 600}
        }
        
        return size_mapping.get(image_type, {"width": 800, "height": 600})
    
    def _get_color_scheme(self, image_type: ImageType) -> List[str]:
        """이미지 유형별 권장 색상 팔레트를 반환합니다."""
        color_mapping = {
            ImageType.FEATURED: ["#2E86AB", "#A23B72", "#F18F01"],
            ImageType.INFOGRAPHIC: ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
            ImageType.CHART: ["#3498DB", "#E74C3C", "#2ECC71", "#F39C12"],
            ImageType.DIAGRAM: ["#34495E", "#E67E22", "#9B59B6", "#1ABC9C"],
            ImageType.SCREENSHOT: ["#FFFFFF", "#F8F9FA", "#E9ECEF"],
            ImageType.ILLUSTRATION: ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"]
        }
        
        return color_mapping.get(image_type, ["#3498DB", "#E74C3C", "#2ECC71"])
    
    def _get_style_guide(self, image_type: ImageType) -> Dict[str, str]:
        """이미지 유형별 스타일 가이드를 반환합니다."""
        style_mapping = {
            ImageType.FEATURED: {
                "font": "Bold, Sans-serif",
                "layout": "Clean, Centered",
                "elements": "Minimal, Focused"
            },
            ImageType.INFOGRAPHIC: {
                "font": "Clear, Readable",
                "layout": "Structured, Hierarchical",
                "elements": "Icons, Charts, Text"
            },
            ImageType.CHART: {
                "font": "Professional, Data-focused",
                "layout": "Grid-based, Aligned",
                "elements": "Bars, Lines, Labels"
            },
            ImageType.DIAGRAM: {
                "font": "Technical, Clear",
                "layout": "Flow-based, Connected",
                "elements": "Shapes, Arrows, Labels"
            },
            ImageType.SCREENSHOT: {
                "font": "System, Native",
                "layout": "As-is, Authentic",
                "elements": "Real interface elements"
            },
            ImageType.ILLUSTRATION: {
                "font": "Creative, Stylized",
                "layout": "Artistic, Free-form",
                "elements": "Custom graphics, Icons"
            }
        }
        
        return style_mapping.get(image_type, {
            "font": "Professional, Clear",
            "layout": "Balanced, Structured",
            "elements": "Clean, Focused"
        })
    
    def _calculate_seo_score(self, 
                           title: str,
                           alt_text: str,
                           caption: str,
                           target_keyword: str,
                           lsi_keywords: List[str]) -> int:
        """SEO 점수를 계산합니다."""
        score = 0
        
        # 제목에 타겟 키워드 포함 여부
        if target_keyword.lower() in title.lower():
            score += 20
        
        # Alt 텍스트에 타겟 키워드 포함 여부
        if target_keyword.lower() in alt_text.lower():
            score += 15
        
        # 캡션에 타겟 키워드 포함 여부
        if target_keyword.lower() in caption.lower():
            score += 10
        
        # LSI 키워드 포함 여부
        if lsi_keywords:
            lsi_count = sum(1 for lsi in lsi_keywords 
                          if lsi.lower() in (title + alt_text + caption).lower())
            score += lsi_count * 5
        
        # Alt 텍스트 길이 점수
        if 50 <= len(alt_text) <= 125:
            score += 10
        elif 25 <= len(alt_text) <= 150:
            score += 5
        
        # 캡션 길이 점수
        if 50 <= len(caption) <= 200:
            score += 10
        elif 25 <= len(caption) <= 250:
            score += 5
        
        return score
    
    def generate_multiple_images(self, 
                                topic: str,
                                target_keyword: str,
                                lsi_keywords: List[str] = None,
                                num_images: int = 3) -> List[Dict[str, any]]:
        """여러 이미지의 메타데이터를 생성합니다."""
        image_types = [
            ImageType.FEATURED,
            ImageType.INFOGRAPHIC,
            ImageType.CHART
        ]
        
        images = []
        for i in range(min(num_images, len(image_types))):
            image_type = image_types[i]
            metadata = self.generate_image_metadata(
                topic, target_keyword, lsi_keywords, image_type
            )
            images.append(metadata)
        
        return images

# 사용 예시
if __name__ == "__main__":
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
    
    # 결과 출력
    print("=== 생성된 이미지 메타데이터 ===")
    print(f"제목: {metadata['title']}")
    print(f"Alt 텍스트: {metadata['alt_text']}")
    print(f"캡션: {metadata['caption']}")
    print(f"메타 설명: {metadata['meta_description']}")
    print(f"파일명: {metadata['filename']}")
    print(f"SEO 점수: {metadata['seo_score']}")
    print(f"권장 크기: {metadata['recommended_size']}")
    print(f"색상 팔레트: {metadata['color_scheme']}")
    print(f"스타일 가이드: {metadata['style_guide']}")
    print()
    
    # 여러 이미지 생성
    print("=== 여러 이미지 생성 ===")
    multiple_images = generator.generate_multiple_images(
        topic="성공하는 방법",
        target_keyword="마케팅",
        lsi_keywords=["디지털", "온라인", "전략"],
        num_images=3
    )
    
    for i, img in enumerate(multiple_images, 1):
        print(f"{i}. {img['title']} (SEO: {img['seo_score']})")