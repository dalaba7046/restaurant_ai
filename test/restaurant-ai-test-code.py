#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
餐廳AI記帳系統 - 配置文件版本
使用外部 config.json 管理所有配置
"""

import json
import re
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import base64

class ConfigManager:
    """配置管理器 - Linus 認可的單一職責設計"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路徑
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {self.config_path}")
            print("提示: 請確保 config.json 在程式執行目錄")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式錯誤: {str(e)}")
            raise
    
    def _validate_config(self) -> None:
        """驗證配置完整性"""
        required_keys = ["models", "api", "prompts", "parameters", "settlement_rules"]
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"配置文件缺少必要欄位: {key}")
        
        # 驗證模型配置
        if "text" not in self.config["models"] or "image" not in self.config["models"]:
            raise ValueError("配置文件缺少模型定義: text 或 image")
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """
        獲取配置值（支援多層級訪問）
        
        Examples:
            config.get("models", "text")  → "google/gemma-3-1b"
            config.get("api", "endpoint") → "http://localhost:1234/..."
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def get_prompt(self, prompt_type: str, **kwargs) -> str:
        """
        獲取提示詞並替換佔位符
        
        Args:
            prompt_type: 提示詞類型（text_system / image_system）
            **kwargs: 用於替換的變數
        
        Returns:
            格式化後的提示詞
        """
        template = self.get("prompts", prompt_type)
        if template is None:
            raise ValueError(f"未找到提示詞: {prompt_type}")
        
        # 替換佔位符
        return template.format(**kwargs)


class RestaurantAI:
    """餐廳AI記帳處理器 - 配置外部化版本"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化AI處理器
        
        Args:
            config_path: 配置文件路徑
        """
        # ✅ 使用配置管理器（單一職責）
        self.config = ConfigManager(config_path)
        self.test_results = []
        
        # 從配置載入 API 端點
        self.api_url = self.config.get("api", "endpoint")
        
        print(f"✅ 配置已載入: {config_path}")
        print(f"  文字模型: {self.config.get('models', 'text')}")
        print(f"  圖片模型: {self.config.get('models', 'image')}")
        print(f"  API端點: {self.api_url}")
    
    def process_text_lm_studio(self, user_input: str) -> Dict[str, Any]:
        """使用配置文件中的設定處理文字輸入"""
        
        # ✅ 從配置獲取提示詞（支援變數替換）
        try:
            prompt = self.config.get_prompt("text_system", user_input=user_input)
        except Exception as e:
            return {
                "success": False,
                "error": f"提示詞生成失敗: {str(e)}"
            }
        
        # ✅ 從配置獲取模型和參數
        model = self.config.get("models", "text")
        params = self.config.get("parameters", "text")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.1),
            "max_tokens": params.get("max_tokens", 200),
            "stop": params.get("stop", [])
        }
        
        return self._call_api(payload, "text")
    
    def process_image_lm_studio(self, image_path: str) -> Dict[str, Any]:
        """使用配置文件中的設定處理圖片輸入"""
        
        # 讀取並編碼圖片
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            return {"success": False, "error": f"圖片讀取失敗: {str(e)}"}
        
        # ✅ 從配置獲取提示詞
        try:
            prompt = self.config.get_prompt("image_system")
        except Exception as e:
            return {
                "success": False,
                "error": f"提示詞生成失敗: {str(e)}"
            }
        
        # ✅ 從配置獲取模型和參數
        model = self.config.get("models", "image")
        params = self.config.get("parameters", "image")
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        }
                    ]
                }
            ],
            "temperature": params.get("temperature", 0.1),
            "max_tokens": params.get("max_tokens", 300)
        }
        
        return self._call_api(payload, "image")
    
    def _call_api(self, payload: Dict[str, Any], input_type: str) -> Dict[str, Any]:
        """
        統一的 API 調用邏輯（消除重複代碼）
        
        Args:
            payload: API 請求內容
            input_type: 輸入類型（text/image）
        """
        timeout = self.config.get("api", "timeout", default=60)
        
        try:
            start_time = time.time()
            response = requests.post(self.api_url, json=payload, timeout=timeout)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                raw_content = result["choices"][0]["message"]["content"]
                
                return {
                    "success": True,
                    "model_used": payload["model"],
                    "input_type": input_type,
                    "raw_output": raw_content,
                    "processed_result": self.clean_output(raw_content),
                    "processing_time": end_time - start_time,
                    "tokens_used": result.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"API錯誤: {response.status_code}",
                    "raw_response": response.text
                }
        
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"請求超時（>{timeout}秒）"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"請求失敗: {str(e)}"
            }
    
    def clean_output(self, raw_output: str) -> Dict[str, Any]:
        """清理AI輸出，提取JSON部分"""
        
        cleaned = raw_output.strip()
        
        # 移除常見的多餘文字
        remove_patterns = [
            r'^已收\s*', r'^應收\s*',
            r'^說明：.*?\n', r'^解釋：.*?\n',
            r'^答案：\s*', r'\n已收$', r'\n應收$'
        ]
        
        for pattern in remove_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE)
        
        # 提取JSON
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            json_str = json_match.group().strip()
            try:
                return {"success": True, "data": json.loads(json_str)}
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"JSON解析錯誤: {str(e)}",
                    "json_str": json_str
                }
        else:
            return {"success": False, "error": "未找到JSON格式"}
    
    def validate_result(self, result: Dict[str, Any], expected_amount: float = None) -> Dict[str, Any]:
        """驗證AI輸出結果"""
        
        validation = {"valid": True, "issues": []}
        
        if not result.get("success", False):
            validation["valid"] = False
            validation["issues"].append("處理失敗")
            return validation
        
        data = result.get("data", {})
        transactions = data.get("transactions", [])
        
        if not transactions:
            validation["valid"] = False
            validation["issues"].append("沒有找到交易記錄")
            return validation
        
        for i, trans in enumerate(transactions):
            # 檢查必要欄位
            required_fields = ["type", "category", "amount", "status"]
            for field in required_fields:
                if field not in trans:
                    validation["issues"].append(f"交易{i+1}缺少{field}欄位")
                    validation["valid"] = False
            
            # 檢查金額
            if expected_amount and trans.get("amount") != expected_amount:
                validation["issues"].append(
                    f"金額錯誤: 期望{expected_amount}, 實際{trans.get('amount')}"
                )
            
            # ✅ 使用配置中的業務規則驗證
            category = trans.get("category", "")
            status = trans.get("status", "")
            expected_status = self.get_expected_status(category)
            
            if status != expected_status:
                validation["issues"].append(
                    f"狀態可能錯誤: {category}應該是{expected_status}, 實際是{status}"
                )
        
        return validation
    
    def get_expected_status(self, category: str) -> str:
        """從配置文件獲取預期狀態"""
        rules = self.config.get("settlement_rules")
        if rules and category in rules:
            return rules[category].get("status", "已付")
        return "已付"
    
    def get_model_info(self) -> Dict[str, str]:
        """取得當前使用的模型資訊"""
        return {
            "text_model": self.config.get("models", "text"),
            "image_model": self.config.get("models", "image"),
            "api_endpoint": self.api_url,
            "config_file": self.config.config_path
        }
    
    def reload_config(self) -> bool:
        """
        重新載入配置文件（不需重啟程式）
        
        Returns:
            是否成功重新載入
        """
        try:
            old_config_path = self.config.config_path
            self.config = ConfigManager(old_config_path)
            self.api_url = self.config.get("api", "endpoint")
            print(f"✅ 配置已重新載入: {old_config_path}")
            return True
        except Exception as e:
            print(f"❌ 配置重新載入失敗: {str(e)}")
            return False


def main():
    """主測試函數"""
    
    print("餐廳AI記帳系統 - 配置文件版本")
    print("=" * 70)
    
    # 初始化（會自動讀取 config.json）
    try:
        ai = RestaurantAI()
    except Exception as e:
        print(f"\n初始化失敗: {str(e)}")
        print("\n請確保 config.json 存在且格式正確")
        return
    
    # 檢查 LM Studio 連接
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            print("\n✅ LM Studio 連接正常")
            
            models_data = response.json()
            if "data" in models_data:
                loaded_models = [m.get("id") for m in models_data["data"]]
                print(f"✅ 已載入模型: {', '.join(loaded_models)}")
        else:
            print("\n❌ LM Studio 連接異常")
            return
    except:
        print("\n❌ 無法連接到 LM Studio")
        return
    
    # 測試選單
    while True:
        print("\n" + "=" * 70)
        print("請選擇測試選項:")
        print("1. 文字輸入測試")
        print("2. 圖片輸入測試")
        print("3. 查看模型資訊")
        print("4. 重新載入配置（不重啟程式）")
        print("5. 查看當前配置內容")
        print("0. 退出")
        
        choice = input("\n請輸入選項 (0-5): ").strip()
        
        if choice == "1":
            user_input = input("請輸入測試文字: ").strip()
            if user_input:
                print(f"\n使用模型: {ai.config.get('models', 'text')}")
                result = ai.process_text_lm_studio(user_input)
                
                print("\n=== 測試結果 ===")
                print(f"模型: {result.get('model_used', 'N/A')}")
                print(f"原始輸出: {result.get('raw_output')}")
                print(f"處理時間: {result.get('processing_time', 0):.2f}秒")
                
                if result.get("success"):
                    validation = ai.validate_result(result)
                    print(f"驗證結果: {'✅ 通過' if validation['valid'] else '❌ 失敗'}")
                    if validation["issues"]:
                        for issue in validation["issues"]:
                            print(f"  ⚠️ {issue}")
        
        elif choice == "2":
            image_path = input("請輸入圖片路徑: ").strip()
            if image_path and Path(image_path).exists():
                print(f"\n使用模型: {ai.config.get('models', 'image')}")
                result = ai.process_image_lm_studio(image_path)
                
                print("\n=== 圖片測試結果 ===")
                print(f"模型: {result.get('model_used', 'N/A')}")
                print(f"原始輸出: {result.get('raw_output')}")
                print(f"處理時間: {result.get('processing_time', 0):.2f}秒")
            else:
                print("圖片檔案不存在！")
        
        elif choice == "3":
            info = ai.get_model_info()
            print("\n=== 模型配置資訊 ===")
            print(f"配置文件: {info['config_file']}")
            print(f"文字處理: {info['text_model']}")
            print(f"圖片處理: {info['image_model']}")
            print(f"API端點: {info['api_endpoint']}")
        
        elif choice == "4":
            print("\n重新載入配置中...")
            if ai.reload_config():
                print("提示: 提示詞和參數已更新，不需重啟程式")
            else:
                print("提示: 配置載入失敗，繼續使用舊配置")
        
        elif choice == "5":
            print("\n=== 當前配置摘要 ===")
            print(f"文字模型: {ai.config.get('models', 'text')}")
            print(f"圖片模型: {ai.config.get('models', 'image')}")
            print(f"溫度（文字）: {ai.config.get('parameters', 'text', 'temperature')}")
            print(f"溫度（圖片）: {ai.config.get('parameters', 'image', 'temperature')}")
            
            rules = ai.config.get("settlement_rules")
            print(f"\n業務規則數量: {len(rules) if rules else 0}")
            if rules:
                print("支援的分類:")
                for category, rule in rules.items():
                    print(f"  - {category}: {rule['status']} (入帳{rule['delay_days']}天)")
        
        elif choice == "0":
            print("退出測試程式")
            break
        
        else:
            print("無效選項，請重新輸入")


if __name__ == "__main__":
    main()
