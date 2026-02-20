#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PPOCR_api import GetOcrApi
import os
import csv
import re
from datetime import datetime

def filter_text_blocks(text_blocks, remove_numbers=True, min_confidence=0.75):
    filtered_blocks = []
    for block in text_blocks:
        text = block.get('text', '')
        score = block.get('score', 0)
        if score < min_confidence:
            continue
        if remove_numbers and re.search(r'\d', text):
            continue
        text_cleaned = re.sub(r'[\u4e00-\u9fff]+', '', text).strip()
        if text_cleaned:
            block_copy = block.copy()
            block_copy['text'] = text_cleaned
            filtered_blocks.append(block_copy)
    return filtered_blocks


def sort_blocks_grid(blocks, column_first=True):
    sorted_blocks = []
    for block in blocks:
        box = block.get('box', [])
        if len(box) >= 2:
            x_center = (box[0][0] + box[2][0]) / 2
            y_center = (box[0][1] + box[2][1]) / 2
            block_copy = block.copy()
            block_copy['_x'] = x_center
            block_copy['_y'] = y_center
            sorted_blocks.append(block_copy)
    
    if column_first:
        sorted_blocks.sort(key=lambda b: b['_x'])
        columns = []
        current_column = [sorted_blocks[0]]
        x_threshold = 100
        
        for block in sorted_blocks[1:]:
            if abs(block['_x'] - current_column[-1]['_x']) < x_threshold:
                current_column.append(block)
            else:
                current_column.sort(key=lambda b: b['_y'])
                columns.append(current_column)
                current_column = [block]
        
        if current_column:
            current_column.sort(key=lambda b: b['_y'])
            columns.append(current_column)
        
        sorted_blocks = []
        for col in columns:
            sorted_blocks.extend(col)
    else:
        sorted_blocks.sort(key=lambda b: b['_y'])
        rows = []
        current_row = [sorted_blocks[0]]
        y_threshold = 50
        
        for block in sorted_blocks[1:]:
            if abs(block['_y'] - current_row[-1]['_y']) < y_threshold:
                current_row.append(block)
            else:
                current_row.sort(key=lambda b: b['_x'])
                rows.append(current_row)
                current_row = [block]
        
        if current_row:
            current_row.sort(key=lambda b: b['_x'])
            rows.append(current_row)
        
        sorted_blocks = []
        for row in rows:
            sorted_blocks.extend(row)
    
    return sorted_blocks


def transpose_list(text_list, rows, cols):
    if len(text_list) != rows * cols:
        total = len(text_list)
        cols = cols or int(total ** 0.5)
        rows = (total + cols - 1) // cols
    
    matrix = []
    for i in range(0, len(text_list), cols):
        row = text_list[i:i+cols]
        if len(row) < cols:
            row.extend([''] * (cols - len(row)))
        matrix.append(row)
    
    transposed = []
    for col in range(cols):
        for row in range(rows):
            if row < len(matrix) and col < len(matrix[row]):
                text = matrix[row][col]
                if text:
                    transposed.append(text)
    
    return transposed


def main():
    
    USE_ENGLISH_MODEL = True
    REMOVE_NUMBERS = True
    MIN_CONFIDENCE = 0.75
    TRANSPOSE = True
    GRID_ROWS = 3
    GRID_COLS = 4
    import sys
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
        parent_dir = current_dir
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
    
    print(f"当前目录：{parent_dir}")
    
    ocr_exe_path = os.path.join(parent_dir, "lib", "model.exe")
    image_dir = os.path.join(parent_dir, "image")
    
    if not os.path.exists(ocr_exe_path):
        print(f"   请确保 lib 文件夹在程序目录下")
        return
    
    if not os.path.exists(image_dir):
        print(f"\n错误：找不到图片文件夹")
        print(f"   请在程序目录下创建 image 文件夹")
        return
    
    image_files = [f for f in os.listdir(image_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    image_files.sort()
    
    if not image_files:
        return

    print("初始化OCR引擎...")
    argument = {}
    if USE_ENGLISH_MODEL:
        models_dir = os.path.join(parent_dir, "lib", "models")
        config_en = os.path.join(models_dir, "config_en.txt")
        if os.path.exists(config_en):
            argument = {'config_path': 'models/config_en.txt'}
    
    try:
        ocr = GetOcrApi(ocr_exe_path, argument=argument)
    except Exception as e:
        return
    
    print("\n" + "=" * 70)
    print("开始识别...")
    print("=" * 70)
    
    csv_data = []
    csv_data.append(['文件名', '识别文本'])
    
    for idx, image_file in enumerate(image_files, 1):
        image_path = os.path.join(image_dir, image_file)
        print(f"\n[{idx}/{len(image_files)}] {image_file}")
        
        try:
            result = ocr.run(image_path)
            
            if result['code'] == 100:
                text_blocks_raw = result['data']
                print(f"  识别: {len(text_blocks_raw)} 个文本块", end=" -> ")
                
                text_blocks_filtered = filter_text_blocks(
                    text_blocks_raw, 
                    remove_numbers=REMOVE_NUMBERS,
                    min_confidence=MIN_CONFIDENCE
                )
                print(f"过滤: {len(text_blocks_filtered)} 个", end=" -> ")
                
                if len(text_blocks_filtered) > 0:
                    text_blocks_sorted = sort_blocks_grid(text_blocks_filtered, column_first=True)
                    
                    texts = [b.get('text', '') for b in text_blocks_sorted]
                    
                    if TRANSPOSE and len(texts) == GRID_ROWS * GRID_COLS:
                        texts = transpose_list(texts, GRID_ROWS, GRID_COLS)
                       
                    else:
                        print(f"完成: {len(texts)} 个")
                    
                    if len(texts) != 12:
                        csv_data.append([image_file, '异常'])
                        print(f"  异常")
                    else:
                        combined_text = '|'.join(texts)
                        csv_data.append([image_file, combined_text])
                        print(f"  结果: {combined_text[:80]}" + ("..." if len(combined_text) > 80 else ""))
                else:
                    print("无有效文本")
                    csv_data.append([image_file, ''])
            else:
                print(f"  识别失败")
                csv_data.append([image_file, ''])
        
        except Exception as e:  
            csv_data.append([image_file, ''])
    
    ocr.exit()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = os.path.join(parent_dir, f"ocr_results_{timestamp}.csv")
    
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    print(f"保存路径：{csv_file}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n程序错误：{e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n按回车键退出...")

