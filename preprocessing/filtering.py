import json
import os
import cv2
import numpy as np

# 1. Đọc danh sách ảnh trùng đã export
with open("unique_images.json", "r", encoding="utf-8") as f:
    unique_set = set(json.load(f))

# 2. Duyệt qua toàn bộ ảnh nguồn để lọc chất lượng (blur, exposure...)
input_dir = "images/1"
output_clean_dir = "filtered_images/clean"
os.makedirs(output_clean_dir, exist_ok=True)

def crop_circular_roi(image, tol=15):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, tol, 255, cv2.THRESH_BINARY)
    
    # Loại nhiễu nhỏ bằng Closing
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image
        
    largest_contour = max(contours, key=cv2.contourArea)
    (cx, cy), radius = cv2.minEnclosingCircle(largest_contour)
    
    # Cạnh của hình vuông nội tiếp bên trong đường tròn: a = r * sqrt(2)
    # Nhân hệ số an toàn 0.95 để đảm bảo không bị chạm mép đen
    side = int(radius * 1.4142 * 0.95)
    half_side = side // 2
    
    h, w = image.shape[:2]
    x1 = max(0, int(cx - half_side))
    y1 = max(0, int(cy - half_side))
    x2 = min(w, int(cx + half_side))
    y2 = min(h, int(cy + half_side))
    
    # Trả về ảnh đã cắt sạch mép
    cropped = image[y1:y2, x1:x2]
    return cropped if cropped.size > 0 else image

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

            # Nếu không trùng -> Tiếp tục chạy hàm QC (Blur)
            img = cv2.imread(relative_path)
            
            # Cắt bỏ viền đen (Vignetting / Black Border Removal)    
            clean_img = crop_circular_roi(img)
            save_path = os.path.join(output_clean_dir, file)
            cv2.imwrite(save_path, clean_img)
            print(f"Đã lưu ảnh sạch (đã cắt viền): {file}")
            
def evaluate_image_quality(cropped_image, blur_threshold=100.0, max_highlight_ratio=0.08):
    """
    Đầu vào là ảnh đã được cắt bỏ viền đen
    """
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    
    # 1. Phát hiện đốm chói lóa (Specular Highlights)
    hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]
    highlight_mask = v_channel > 240
    
    highlight_ratio = np.sum(highlight_mask) / (cropped_image.shape[0] * cropped_image.shape[1])
    if highlight_ratio > max_highlight_ratio:
        # Loại nếu diện tích phản quang/chói sáng quá lớn (> 8%)
        return False, 0.0, f"Over-exposed / Specular: {highlight_ratio:.2%}"

    # 2. Tính Laplacian chỉ trên vùng niêm mạc hợp lệ (loại pixel chói và pixel quá tối)
    valid_tissue_mask = (gray > 20) & (~highlight_mask)
    if np.sum(valid_tissue_mask) < 0.2 * gray.size:
        return False, 0.0, "Too few valid pixels"

    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    # Lấy các giá trị Laplacian nằm trong vùng mô hợp lệ
    lap_vals = laplacian[valid_tissue_mask]
    blur_score = float(np.var(lap_vals))
    
    is_sharp = blur_score >= blur_threshold
    return is_sharp, blur_score, "Passed" if is_sharp else "Blurry"
  
input_dir_vignetted = "filtered_images/clean"
output_clean_dir = "filtered_vig_images/clean"
os.makedirs(output_clean_dir, exist_ok=True)


for root, _, files in os.walk(input_dir_vignetted):
    for file in files:
        if file.lower().endswith(('.jpg', '.png', '.jpeg')):
            # Lấy đường dẫn chuẩn hóa
            relative_path = os.path.relpath(os.path.join(root, file), start=".")
            # Chuẩn hóa dấu gạch chéo để tương thích giữa Windows/Linux
            relative_path = relative_path.replace("\\", "/")
            # Nếu không trùng -> Tiếp tục chạy hàm QC (Blur)
            img = cv2.imread(relative_path)
            clean_img = evaluate_image_quality(img, blur_threshold=100.0, max_highlight_ratio=0.08)
            if (clean_img): 
                save_path = os.path.join(output_clean_dir, file)
                cv2.imwrite(save_path, img)
                print(f"Đã lưu ảnh sạch đã cắt viền và kiểm tra chất lượng: {file}")
            else:
                print(f"Chất lượng ảnh không đủ tốt: {file}")