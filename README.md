# Handwrite
## Features  
- 能夠將文章隨機轉換為預先設定的手寫字，但同時允許用戶自己調整
- 將手寫字匯出成pdf 
- 嘗試模擬筆記軟體的風格（如背景）

## Install
1. 下載專案
```bash
git clone git@github.com:yushiuan9499/handwrite.git

```
2. 進入專案資料夾
```bash
cd handwrite
```
3. 安裝依賴
```bash
pip install -r requirements.txt
```

## Usage
### 設定字形
- 將字的.svg檔案放在`data/font/<word>`資料夾中  
  例如`範`這個字就放在`data/font/範/`資料夾中

### 執行
```bash
python main.py
```

