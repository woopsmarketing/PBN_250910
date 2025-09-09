import sys
from types import ModuleType

# 만약 이미 존재하면 건너뛰고, 없으면 dummy 모듈 생성
if "pydantic.deprecated.decorator" not in sys.modules:
    dummy_module = ModuleType("pydantic.deprecated.decorator")
    dummy_module.__all__ = []  # 빈 모듈로 설정
    sys.modules["pydantic.deprecated.decorator"] = dummy_module
