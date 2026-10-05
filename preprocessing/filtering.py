import json
import os
import cv2

# 1. Đọc danh sách ảnh trùng đã export
with open("unique_images.json", "r", encoding="utf-8") as f:
    unique_set = set(json.load(f))

# 2. Duyệt qua toàn bộ ảnh nguồn để lọc chất lượng (blur, exposure...)
input_dir = "images/1"
output_clean_dir = "filtered_images/clean"
os.makedirs(output_clean_dir, exist_ok=True)

def check_blur(image, threshold=40.0):
    # Chuyển ảnh sang thang xám
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Tính phương sai của toán tử Laplacian
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    # True nếu ảnh đủ độ nét, False nếu ảnh bị mờ nhòe
    return score >= threshold, score

def crop_black_border_bbox(image, tol=15):
    """
    image: ảnh màu BGR đọc từ cv2.imread
    tol: ngưỡng độ sáng để coi là màu đen (mặc định <= 15)
    """
    # 1. Chuyển sang ảnh thang xám
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. Tạo mặt nạ nhị phân: pixel > tol là vùng niêm mạc (trắng), còn lại là viền đen
    _, mask = cv2.threshold(gray, tol, 255, cv2.THRESH_BINARY)
    
    # 3. Lọc nhiễu bằng phép đóng hình thái học (Morphological Closing)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 4. Tìm đường viền lớn nhất (chính là vùng nội soi)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image  # Trả về ảnh gốc nếu không tìm thấy contour
        
    largest_contour = max(contours, key=cv2.contourArea)
    
    # 5. Lấy tọa độ hộp bao giới hạn (x, y, w, h)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Cắt ảnh
    cropped = image[y:y+h, x:x+w]
    return cropped

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
            
            # Cắt bỏ viền đen (Vignetting / Black Border Removal)    
            
            if is_sharp:
                clean_img = crop_black_border_bbox(img)
                save_path = os.path.join(output_clean_dir, file)
                cv2.imwrite(save_path, clean_img)
                print(f"Đã lưu ảnh sạch (đã cắt viền): {file}")