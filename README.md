# Restaurant AI

本專案旨在開發一個智慧化的自動記帳與分類系統，支援文字與圖片輸入。\
系統可協助餐飲店家自動化處理日常的收支記錄，並進行分類與分析。

------------------------------------------------------------------------

## 📌 功能特色

-   **多模態輸入**
    -   支援自然語言文字輸入（基於 `google/gemma-3-1b`）。
    -   支援收據、餐飲單據照片輸入（基於 `qwen2-vl-7b-instruct`）。
-   **自動分類**
    -   區分支出（食材、租金、薪資等）。
    -   區分營收來源（現金、信用卡、外送平台如
        UberEats、Foodpanda、團膳等）。
-   **結構化輸出**
    -   透過提示詞 (Prompt) 設計，輸出 JSON/CSV
        格式，便於後續整合到報表或會計系統。
-   **可擴展性**
    -   模組化設計，方便替換不同的 LLM 或多模態模型。
    -   可本地部署，也可串接雲端 API（如 OpenAI GPT、Anthropic
        Claude）。

------------------------------------------------------------------------

## 📂 專案結構建議

    restaurant_ai/
    ├── data/                 # 測試數據與範例收據
    ├── notebooks/            # 模型測試與原型開發 Jupyter Notebooks
    ├── src/                  # 核心程式碼
    │   ├── __init__.py
    │   ├── text_module/      # NLP 處理 (gemma)
    │   ├── vision_module/    # 圖像處理 (qwen2-vl)
    │   ├── pipelines/        # 任務流程 (文字/圖片 -> JSON)
    │   ├── utils/            # 工具函式 (格式轉換、日誌等)
    │   └── config.py         # 系統設定
    ├── tests/                # 測試程式
    ├── requirements.txt      # 套件需求
    ├── README.md             # 專案說明文件
    └── LICENSE

------------------------------------------------------------------------

## 🚀 快速開始

### 1. 安裝環境

``` bash
git clone https://github.com/dalaba7046/restaurant_ai.git
cd restaurant_ai
pip install -r requirements.txt
```

### 2. 測試文字模型

``` bash
python src/text_module/test_gemma.py --input "今天收入 UberEats 2500 元"
```

### 3. 測試圖片模型

``` bash
python src/vision_module/test_qwen2vl.py --image ./data/receipt.jpg
```

### 4. 輸出結果

系統會將解析後的結果輸出為 JSON，例如：

``` json
{
  "type": "revenue",
  "source": "UberEats",
  "amount": 2500,
  "date": "2025-09-24"
}
```

------------------------------------------------------------------------

## 🔧 未來規劃

-   [ ] 加入語音輸入模組（結合 OpenAI Whisper 或其他 ASR 模型）。
-   [ ] 建立 Web UI（Streamlit / Gradio）。
-   [ ] 串接雲端平台（GCP / AWS / Azure）。
-   [ ] 自動產出財務報表與分析。

------------------------------------------------------------------------

## 📜 授權

本專案採用 MIT License。
