# Endoscopic Vision: Anomaly Detection & Diagnostic Framework

Hệ thống thị giác máy tính hỗ trợ phát hiện các điểm bất thường và chẩn đoán tổn thương niêm mạc (viêm loét, polyp, xuất huyết) trên ảnh và video nội soi tiêu hóa.

---

## 📌 Project Roadmap & Scope

Dự án được chia thành các giai đoạn mô-đun hóa:
- [x] **Phase 1: Data Engineering & Cleaning (Giai đoạn hiện tại)**
  - Trích xuất frame từ video nội soi độ phân giải cao.
  - Tự động nhận diện và loại bỏ nhiễu: viền đen màn hình, lóa sáng phản xạ (specular reflection), bọt khí/dịch nhầy, frame bị mờ do chuyển động (motion blur).
  - Chuẩn hóa phân phối màu sắc và kích thước theo bệnh nhân (Patient-wise splitting).
- [ ] **Phase 2: Representation Learning & Feature Extraction**
  - Huấn luyện Self-supervised learning (Contrastive Learning / Masked Autoencoders) trên dữ liệu nội soi không nhãn.
- [ ] **Phase 3: Anomaly Detection & Lesion Localization**
  - Ứng dụng Unsupervised Anomaly Detection (Reconstruction error / Embedding density).
  - Phân đoạn tổn thương (Semantic Segmentation).
- [ ] **Phase 4: Temporal Video-level Inference**
  - Tích hợp mô hình chuỗi (LSTM/Transformer) để lọc false-positive giữa các frame liên tiếp.

---

## ⚙️ Cài đặt môi trường

```bash
git clone [https://github.com/username/endoscopy-analysis.git](https://github.com/username/endoscopy-analysis.git)
cd endoscopy-analysis
pip install -r requirements.txt
```

---

## 📂 Hướng dẫn Tiền xử lý dữ liệu (Phase 1)

### 1. Chuẩn bị dữ liệu
Đặt video gốc hoặc thư mục ảnh chụp thô vào `data/raw/` theo cấu trúc:
```text
data/raw/
├── patient_001/
│   └── video_colonoscopy_01.mp4
└── patient_002/
    ├── img_001.png
    └── img_002.png
```

### 2. Trích xuất frame từ video
Trích xuất khung hình tự động theo tần suất fps cấu hình:
```bash
python scripts/extract_frames.py --config configs/data/frame_extraction.yaml
```

### 3. Chạy Pipeline làm sạch và lọc nhiễu
Thực thi pipeline loại bỏ ảnh kém chất lượng và crop vùng ROI:
```bash
python scripts/run_cleaning.py --input-dir data/interim/frames --output-dir data/processed
```
*Các bước xử lý tự động:*
- **ROI Cropping:** Tự động cắt bỏ viền đen và thông số metadata hiển thị trên màn hình nội soi.
- **Blur Detection:** Đo phương sai toán tử Laplacian ($\text{Var}(\text{Laplacian}) < \tau$).
- **Reflection & Specular Removal:** Đo ngưỡng bão hòa kênh màu để phát hiện vệt bóng của đèn nội soi.

### 4. Tạo file Dataset Manifest
```bash
python scripts/generate_metadata_manifest.py --output data/processed/manifest.csv
```

---

## 📊 Phân chia tập dữ liệu (Dataset Splitting Policy)

Để tránh hiện tượng **Data Leakage**, dữ liệu luôn được chia ở **cấp độ bệnh nhân (Patient-level)**:
- Train: 70% bệnh nhân
- Validation: 15% bệnh nhân
- Test: 15% bệnh nhân
*(Tuyệt đối không trộn lẫn các frame từ cùng một ca nội soi vào cả 2 tập Train và Test).*
