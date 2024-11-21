import os
import shutil

# 定义原始文件夹路径和目标文件夹路径
source_folder = 'D:\zancun\pdf'  #原始文件夹
target_folder = 'D:\pdf2222'  #新文件夹

# 如果目标文件夹不存在，则创建
if not os.path.exists(target_folder):
    os.makedirs(target_folder)

# 使用 os.walk() 递归遍历所有子文件夹
for root, dirs, files in os.walk(source_folder):
    for filename in files:
        # 检查文件是否以".pdf"结尾
        if filename.endswith('.pdf'):
            # 构造完整的文件路径
            source_file = os.path.join(root, filename)
            target_file = os.path.join(target_folder, filename)

            # 如果文件名重复，添加索引后缀避免覆盖
            if os.path.exists(target_file):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_file):
                    target_file = os.path.join(target_folder, f"{base}_{counter}{ext}")
                    counter += 1

            # 将PDF文件复制到目标文件夹
            shutil.copy(source_file, target_file)
            print(f"已复制: {filename} 到 {target_file}")

print("筛选并复制PDF文件完成。")
