# tools/word_csv_to_json.py
import csv
import json
import uuid
from typing import List, Dict, Optional
import codecs


def convert_csv_to_json(csv_file_path: str, json_file_path: str):
    """
    读取CSV文件，转换为JSON格式并写入到JSON文件。

    Args:
        csv_file_path: CSV文件的路径。
        json_file_path: JSON文件的路径。
    """
    word_dict: Dict[str, Dict] = {}
    with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
        # 读取文件头，检查BOM 并移除
        header = csvfile.readline()
        if header.startswith(codecs.BOM_UTF8.decode("utf-8")):
            header = header[1:]

        # 使用strip()删除开头和结尾的空白字符，并分割获取列名
        fieldnames = [name.strip() for name in header.strip().split(",")]

        csv_reader = csv.DictReader(csvfile, fieldnames=fieldnames)

        for row in csv_reader:
            word = row["词语"].strip()  # 去除词语首尾的空格
            part_of_speech = (
                row["词性"].strip() if row.get("词性") else None
            )  # 获取词性
            # key 由 词语和词性组合而成
            key = f"{word}-{part_of_speech}"

            chaotong_level = int(row["级别"]) if row.get("级别") else None
            hsk_level = (
                float(row.get("HSK词语级别", None))
                if row.get("HSK词语级别", None)
                else None
            )

            if key not in word_dict:
                word_dict[key] = {
                    "word_id": str(uuid.uuid4()),
                    "word": word,
                    "chaotong_level": chaotong_level,
                    "hsk_level": hsk_level,
                    "part_of_speech": part_of_speech,
                }
            else:
                existing_word = word_dict[key]
                # 如果词条已经存在，比较 chaotong_level，使用较小的
                if chaotong_level is not None and (
                    existing_word.get("chaotong_level") is None
                    or chaotong_level < existing_word["chaotong_level"]
                ):
                    existing_word["chaotong_level"] = chaotong_level

                if hsk_level is not None:
                    existing_word["hsk_level"] = hsk_level

    data = list(word_dict.values())

    with open(json_file_path, mode="w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    csv_file = "others_docs/words.csv"
    json_file = "app/data/words.json"
    convert_csv_to_json(csv_file, json_file)
    print(f"Successfully converted '{csv_file}' to '{json_file}'")
