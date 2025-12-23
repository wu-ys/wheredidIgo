import os
import re
import glob
import csv
import json

def batch_process_files(folder_path):
    remove_wpt_from_content(folder_path)
    remove_parentheses_from_filenames(folder_path)

def remove_wpt_from_content(folder_path):

    files = glob.glob(os.path.join(folder_path, '**/*.gpx'))

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

    files = glob.glob(os.path.join(folder_path, '**/*.gpx'))

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

def export_railway_gpx_to_csv(folder_path, csv_file_path, json_file_path):

    existing_names = set()
    records = {}

    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get('name_zh')
                name_en = row.get('name_en', "")
                existing_names.add(name)
                records[name] = {"zh": name, "en": name_en}

    new_names = []

    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith('.gpx'):
                filename_without_ext = os.path.splitext(f)[0]
                if filename_without_ext not in existing_names:
                    new_names.append([filename_without_ext])
                    existing_names.add(filename_without_ext)
                    records[filename_without_ext] = {"zh": filename_without_ext, "en": ""}

    if new_names:
        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(new_names)

    print("导出完成！")

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    folder_path = "./railway"
    batch_process_files(folder_path)
    export_railway_gpx_to_csv(folder_path, csv_file_path='./railway/railway.csv', json_file_path='./railway/railway.json')