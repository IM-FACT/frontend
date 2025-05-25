"""
사용자 설정 관리 유틸리티
사용자의 개인 설정을 JSON 파일로 저장하고 관리합니다.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class UserSettings:
    """사용자 설정을 관리하는 클래스"""
    
    def __init__(self, settings_path: str = "user_settings"):
        """
        Args:
            settings_path: 설정 파일을 저장할 디렉토리 경로
        """
        self.settings_path = Path(settings_path)
        self.settings_path.mkdir(exist_ok=True)
        self.settings_file = self.settings_path / "settings.json"
        
        # 기본 설정
        self.default_settings = {
            "profile": {
                "nickname": "사용자",
                "bio": "",
                "avatar_emoji": "👤"
            },
            "preferences": {
                "theme": "light",  # light, dark
                "language": "ko",  # ko, en
                "font_size": "medium",  # small, medium, large
                "response_style": "detailed",  # simple, detailed, academic
                "auto_save": True,
                "show_sources": True,
                "show_timestamps": True
            }
            # 추후 확장 가능한 설정들
            # "notifications": {
            #     "email_notifications": False,
            #     "email": "",
            #     "daily_digest": False,
            #     "weekly_report": False
            # },
            # "api": {
            #     "custom_api_endpoint": "",
            #     "api_key": "",
            #     "use_custom_api": False
            # }
        }
        
        # 설정 초기화
        self._initialize_settings()
    
    def _initialize_settings(self) -> None:
        """설정 파일 초기화"""
        if not self.settings_file.exists():
            self._save_settings(self.default_settings)
    
    def _load_settings(self) -> Dict[str, Any]:
        """설정 로드"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # 누락된 설정 항목이 있으면 기본값으로 채우기
                return self._merge_with_defaults(settings)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_settings.copy()
    
    def _merge_with_defaults(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """기존 설정에 누락된 항목을 기본값으로 채우기"""
        merged = self.default_settings.copy()
        
        def deep_update(base: dict, update: dict) -> dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_update(base[key], value)
                else:
                    base[key] = value
            return base
        
        return deep_update(merged, settings)
    
    def _save_settings(self, settings: Dict[str, Any]) -> None:
        """설정 저장"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """전체 설정 반환"""
        return self._load_settings()
    
    def get_setting(self, category: str, key: Optional[str] = None) -> Any:
        """
        특정 설정 값 반환
        
        Args:
            category: 설정 카테고리 (profile, preferences, notifications, api)
            key: 설정 키 (없으면 전체 카테고리 반환)
            
        Returns:
            설정 값
        """
        settings = self._load_settings()
        
        if category not in settings:
            return None
        
        if key is None:
            return settings[category]
        
        return settings[category].get(key)
    
    def update_setting(self, category: str, key: str, value: Any) -> bool:
        """
        특정 설정 업데이트
        
        Args:
            category: 설정 카테고리
            key: 설정 키
            value: 새 값
            
        Returns:
            성공 여부
        """
        settings = self._load_settings()
        
        if category not in settings:
            return False
        
        settings[category][key] = value
        self._save_settings(settings)
        return True
    
    def update_category(self, category: str, values: Dict[str, Any]) -> bool:
        """
        카테고리 전체 업데이트
        
        Args:
            category: 설정 카테고리
            values: 새 값들
            
        Returns:
            성공 여부
        """
        settings = self._load_settings()
        
        if category not in settings:
            return False
        
        settings[category].update(values)
        self._save_settings(settings)
        return True
    
    # 다음 메서드들은 필요시 활성화 가능
    # def reset_settings(self) -> None:
    #     """설정을 기본값으로 초기화"""
    #     self._save_settings(self.default_settings)
    # 
    # def export_settings(self) -> str:
    #     """설정을 JSON 문자열로 내보내기"""
    #     settings = self._load_settings()
    #     return json.dumps(settings, ensure_ascii=False, indent=2)
    # 
    # def import_settings(self, settings_json: str) -> bool:
    #     """
    #     JSON 문자열에서 설정 가져오기
    #     
    #     Args:
    #         settings_json: JSON 형식의 설정 문자열
    #         
    #     Returns:
    #         성공 여부
    #     """
    #     try:
    #         new_settings = json.loads(settings_json)
    #         # 유효성 검사
    #         if not isinstance(new_settings, dict):
    #             return False
    #         
    #         # 기본값과 병합
    #         merged_settings = self._merge_with_defaults(new_settings)
    #         self._save_settings(merged_settings)
    #         return True
    #     except json.JSONDecodeError:
    #         return False


# 싱글톤 인스턴스
user_settings = UserSettings()
