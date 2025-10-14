import os
import re
import glob

def batch_process_files(folder_path):
    """
    批量处理文件：
    1. 删除文件内容中包含"wpt"的行
    2. 删除文件名中的括号及括号内容
    """
    # 首先处理文件内容
    remove_wpt_from_content(folder_path)
    
    # 然后处理文件名
    remove_parentheses_from_filenames(folder_path)

def remove_wpt_from_content(folder_path):
    """删除文件内容中包含'wpt'的行"""
    print("正在处理文件内容...")
    files = glob.glob(os.path.join(folder_path, '*'))
    
    for file_path in files:
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                filtered_lines = [line for line in lines if 'wpt' not in line]
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(filtered_lines)
                
                print(f"已处理文件内容: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"处理文件内容 {file_path} 时出错: {e}")

def remove_parentheses_from_filenames(folder_path):
    """删除文件名中的括号及括号内容"""
    print("\n正在处理文件名...")
    files = glob.glob(os.path.join(folder_path, '*'))
    
    for file_path in files:
        if os.path.isfile(file_path):
            dir_name = os.path.dirname(file_path)
            old_filename = os.path.basename(file_path)
            
            # 删除括号及括号内容
            new_filename = re.sub(r'\([^)]*\)', '', old_filename)
            # 删除所有空格
            new_filename = new_filename.replace(' ', '')
            
            if new_filename != old_filename:
                new_file_path = os.path.join(dir_name, new_filename)
                
                # 处理文件名冲突
                counter = 1
                temp_new_file_path = new_file_path
                while os.path.exists(temp_new_file_path):
                    name, ext = os.path.splitext(new_file_path)
                    temp_new_file_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                try:
                    os.rename(file_path, temp_new_file_path)
                    print(f"重命名: {old_filename} -> {os.path.basename(temp_new_file_path)}")
                except Exception as e:
                    print(f"重命名 {old_filename} 时出错: {e}")

# 使用方法
folder_path = "./railway"
batch_process_files(folder_path)