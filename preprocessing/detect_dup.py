from PIL import Image
import imagehash
import os
from collections import defaultdict

dataset_path = "images/1"
# image_paths = [os.path.join(dataset_path, f) for f in os.listdir(dataset_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

# image_paths = []
# for root, _, files in os.walk("images"):
#     for f in files:
#         if f.lower().endswith(('.png', '.jpg', '.jpeg')):
#             image_paths.append(os.path.join(root, f).replace("\\", "/"))

image_paths = [
    os.path.join(dataset_path, f).replace("\\", "/") 
    for f in os.listdir(dataset_path) 
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
]

# 1. TÌM ẢNH TRÙNG TUYỆT ĐỐI (Mã băm giống nhau 100%)
hash_dict = defaultdict(list)

for img_path in image_paths:
    try:
        with Image.open(img_path) as img:
            # dhash (Difference Hash) rất tốt cho việc tìm ảnh tương đồng
            h = str(imagehash.dhash(img)) 
            hash_dict[h].append(img_path)
    except Exception as e:
        print(f"Lỗi đọc ảnh {img_path}: {e}")

print("--- CÁC NHÓM ẢNH TRÙNG NHAU TUYỆT ĐỐI ---")
print()
for h, paths in hash_dict.items():
    if len(paths) > 1:
        print(f"Mã băm {h} có các ảnh trùng nhau: {paths}")


# 2. TÌM ẢNH TRÙNG TƯƠNG ĐỐI (Khoảng cách Hamming thấp, ví dụ <= 4)
# (Phương pháp này thu hẹp danh sách bằng cách chỉ so sánh các mã băm duy nhất)
unique_hashes = list(hash_dict.keys())
THRESHOLD = 4  # Độ lệch tối đa để coi là trùng nhau
duplicates_found = []

for i in range(len(unique_hashes)):
    for j in range(i + 1, len(unique_hashes)):
        h1 = imagehash.hex_to_hash(unique_hashes[i])
        h2 = imagehash.hex_to_hash(unique_hashes[j])
        
        # Phép trừ giữa 2 hash trả về khoảng cách Hamming
        if h1 - h2 <= THRESHOLD:
            duplicates_found.append((hash_dict[unique_hashes[i]], hash_dict[unique_hashes[j]]))
            print(f"Kết quả giữa 2 giá trị hash giữa 2 ảnh {hash_dict[unique_hashes[i]]} và {hash_dict[unique_hashes[j]]} là: {float(h1 - h2)}")

print("\n--- CÁC CẶP ẢNH TƯƠNG ĐỒNG NHAU (GẦN GIỐNG) ---")
for item in duplicates_found:
    print(f"Nhóm A: {item[0]} giống Nhóm B: {item[1]}")

import json

# Tập hợp chứa các đường dẫn ảnh bị đánh dấu là bản sao (cần loại bỏ)
duplicates_to_exclude = set()

# Trùng tuyệt đối: giữ lại ảnh đầu tiên paths[0], các ảnh sau là trùng
for h, paths in hash_dict.items():
    if len(paths) > 1:
        for p in paths[1:]:
            duplicates_to_exclude.add(p)

# Trùng tương đối: giữ lại ảnh thuộc nhóm A, đánh dấu toàn bộ ảnh nhóm B là trùng
for group_a, group_b in duplicates_found:
    for p in group_b:
        duplicates_to_exclude.add(p)

# Lấy tập hợp tất cả các ảnh có trong hash_dict
all_images = set()
for paths in hash_dict.values():
    for p in paths:
        all_images.add(p)

# Tập ảnh KHÔNG TRÙNG = Tất cả ảnh - Các ảnh bị trùng
unique_images = list(all_images - duplicates_to_exclude)

# Chuẩn hóa đường dẫn dấu gạch chéo
unique_images = [p.replace("\\", "/") for p in sorted(unique_images)]

# Xuất ra file JSON
output_json = "unique_images.json"
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(unique_images, f, indent=4, ensure_ascii=False)

print(f"\nTổng số ảnh ban đầu: {len(all_images)}")
print(f"Số ảnh bản sao bị loại: {len(duplicates_to_exclude)}")
print(f"Đã xuất thành công {len(unique_images)} ảnh ĐỘC NHẤT (không trùng) vào: {output_json}")