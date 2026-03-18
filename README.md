# CardioViz — Heart Disease Dashboard

> Bài tập lớn môn **Trực quan hóa dữ liệu** — Dashboard phân tích bệnh tim mạch sử dụng Plotly Dash.

## 1. Mô tả bài toán

**Lĩnh vực:** Y tế — Chẩn đoán bệnh tim mạch (Cardiovascular Disease Diagnosis)

**Dataset:** Heart Disease Dataset — Cleveland Clinic Foundation (UCI Machine Learning Repository)
- **Nguồn:** [Kaggle — Heart Disease Dataset](https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset)
- **Kích thước dữ liệu gốc (EDA):** 1.025 dòng × 14 cột
- **Kích thước dữ liệu phân tích (các trang sau EDA):** 302 dòng unique × 14 cột
- **Tiền xử lý:** chuẩn hóa tên cột (`strip`) và loại bỏ dòng trùng lặp (`drop_duplicates`) cho các trang phân tích chính
- **Biến mục tiêu:** `target` (1 = Có bệnh tim, 0 = Không bệnh tim)

**Mục tiêu phân tích:**
- Khám phá và phân tích thống kê mô tả bộ dữ liệu lâm sàng bệnh tim
- Tìm hiểu mối quan hệ giữa các yếu tố nguy cơ (tuổi, cholesterol, huyết áp, nhịp tim, ...) và bệnh tim
- Xây dựng dashboard tương tác đa trang hỗ trợ bác sĩ/nhà phân tích ra quyết định

### Mô tả biến

| Biến | Mô tả | Kiểu |
|---|---|---|
| `age` | Tuổi bệnh nhân (năm) | int |
| `sex` | Giới tính (0 = Nữ, 1 = Nam) | int |
| `cp` | Loại đau ngực (0–3) | int |
| `trestbps` | Huyết áp lúc nghỉ (mmHg) | int |
| `chol` | Cholesterol huyết thanh (mg/dl) | int |
| `fbs` | Đường huyết đói > 120 mg/dl (0/1) | int |
| `restecg` | Kết quả điện tâm đồ nghỉ (0–2) | int |
| `thalach` | Nhịp tim tối đa đạt được (bpm) | int |
| `exang` | Đau ngực khi vận động (0/1) | int |
| `oldpeak` | ST depression do vận động | float |
| `slope` | Slope đoạn ST (0–2) | int |
| `ca` | Số mạch máu lớn phát hiện qua fluoroscopy (0–3) | int |
| `thal` | Thalassemia (1–3) | int |
| `target` | Chẩn đoán bệnh tim (0/1) | int |

## 2. Kiến trúc Dashboard

```
BTL/
├── app.py                    # Entry point — layout, filter, theme toggle
├── heart.csv                 # Dataset
├── requirements.txt          # Dependencies
├── export_charts.py          # Xuất ảnh PNG cho slide
├── assets/
│   └── style.css             # CSS variables + Dash overrides
├── components/
│   ├── sidebar.py            # Sidebar navigation + global filters
│   └── theme.py              # Dark/Light theme palettes
├── pages/
│   ├── page0_eda.py          # Khám Phá Dữ Liệu & EDA
│   ├── page1_overview.py     # Tổng Quan KPI
│   ├── page2_age_trends.py   # Xu Hướng Theo Tuổi
│   ├── page3_clinical.py     # Phân Tích Lâm Sàng
│   ├── page4_correlation.py  # Tương Quan & Feature Importance
│   └── page5_alerts.py       # Cảnh Báo & Chẩn Đoán Cá Nhân
└── exports/                  # Ảnh PNG xuất cho slide (sau khi chạy export)
```

**Công nghệ:**
- **Plotly Dash** — Framework dashboard Python
- **Tailwind CSS** (CDN) — Utility-first CSS
- **DashIconify** — Bộ icon Lucide
- **Pandas / NumPy** — Xử lý dữ liệu
- **Kaleido** — Xuất ảnh tĩnh từ Plotly

## 3. Các trang phân tích

| # | Trang | Đường dẫn | Nội dung chính |
|---|---|---|---|
| 0 | Khám Phá Dữ Liệu | `/eda` | Mô tả dataset, thống kê mô tả, missing values, outlier (IQR), pivot table, data table |
| 1 | Tổng Quan KPI | `/` | 4 KPI cards, donut giới tính, donut chẩn đoán, bar đau ngực, bar mạch tắc |
| 2 | Xu Hướng Tuổi | `/age-trends` | Line+bar tỷ lệ bệnh theo tuổi, boxplot, histogram theo giới, heatmap tuổi×cp |
| 3 | Phân Tích Lâm Sàng | `/clinical-deep-dive` | Histogram+ngưỡng (chol, BP, thalach), stacked 100%, grouped bar (fbs, ecg) |
| 4 | Tương Quan | `/correlation` | Correlation heatmap, feature importance, scatter + trendline |
| 5 | Cảnh Báo Sức Khỏe | `/alerts` | Phân tích nguy cơ cá nhân, waterfall chart, bảng yếu tố, khuyến nghị lâm sàng |

**Tính năng:**
- Sidebar với 4 bộ lọc toàn cục (giới tính, tuổi, đau ngực, chẩn đoán)
- Chế độ Dark / Light theme (lưu localStorage)
- Panel "Nhận Xét & Insight" tự động trên mỗi trang
- Tất cả biểu đồ tương tác (hover, zoom, filter)

## 4. Hướng dẫn chạy

### Yêu cầu
- Python 3.9+
- pip

### Cài đặt

```bash
# Clone repository
git clone <repo-url>
cd BTL

# Tạo virtual environment
python -m venv .venv

# Kích hoạt (Windows)
.venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source .venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Chạy Dashboard

```bash
python app.py
```

Mở trình duyệt tại: **http://localhost:8050**

### Xuất ảnh cho Slide

```bash
# Cài thêm kaleido (nếu chưa có)
pip install kaleido

# Chạy script xuất
python export_charts.py
```

Ảnh PNG sẽ được lưu vào thư mục `exports/` — sẵn sàng cho slide thuyết trình.

## 5. Loại biểu đồ sử dụng

| Loại biểu đồ | Vị trí | Mục đích |
|---|---|---|
| Donut (Pie) | Page 1 | Phân bố giới tính, chẩn đoán |
| Bar chart | Page 0, 1 | Phân bố biến, missing values, outlier |
| Line chart | Page 2 | Xu hướng tỷ lệ bệnh theo tuổi |
| Histogram | Page 2, 3 | Phân phối tuổi, chỉ số lâm sàng |
| Box-plot | Page 0, 2 | Phát hiện outlier, so sánh phân phối |
| Grouped bar | Page 3 | So sánh fbs, restecg giữa 2 nhóm |
| Stacked bar 100% | Page 3 | Nghịch lý đau ngực |
| Heatmap | Page 2, 4 | Tuổi×cp, ma trận tương quan Pearson |
| Scatter + Trendline | Page 4 | Tuổi×nhịp tim, oldpeak×exang |
| Waterfall | Page 5 | Tích lũy yếu tố nguy cơ |
| Subplot (multi-panel) | Page 0 | Boxplot riêng từng biến |
