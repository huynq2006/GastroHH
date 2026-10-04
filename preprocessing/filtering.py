import json
import os
import cv2

# 1. Đọc danh sách ảnh trùng đã export
with open("unique_images.json", "r", encoding="utf-8") as f:
    unique_set = set(json.load(f))

# 2. Duyệt qua toàn bộ ảnh nguồn để lọc chất lượng (blur, exposure...)
input_dir = "images"
output_clean_dir = "filtered_images/clean"
os.makedirs(output_clean_dir, exist_ok=True)

def check_blur(image, threshold=40.0):
    # Chuyển ảnh sang thang xám
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Tính phương sai của toán tử Laplacian
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    # True nếu ảnh đủ độ nét, False nếu ảnh bị mờ nhòe
    return score >= threshold, score

for root, _, files in os.walk(input_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.png', '.jpeg')):
            # Lấy đường dẫn chuẩn hóa
            relative_path = os.path.relpath(os.path.join(root, file), start=".")
            # Chuẩn hóa dấu gạch chéo để tương thích giữa Windows/Linux
            relative_path = relative_path.replace("\\", "/")

            # KIỂM TRA TRỰC TIẾP: Nếu nằm trong danh sách trùng thì bỏ qua luôn
            if relative_path not in unique_set:
                print(f"Bỏ qua ảnh trùng: {relative_path}")
                continue

            # Nếu không trùng -> Tiếp tục chạy các hàm QC (Blur, Specular, Exposure...)
            img = cv2.imread(relative_path)
            # ... thực hiện filtering ...
            is_sharp, _ = check_blur(img, threshold=40.0)
            if is_sharp:
                import shutil
                shutil.copy(relative_path, os.path.join(output_clean_dir, file))