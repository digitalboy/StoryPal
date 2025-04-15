import requests
import json
import argparse

# API 基础 URL
BASE_URL = "http://106.52.130.188:8889/content/getContentListById"

def get_story_details(story_id: str, story_type: int = 2):
    """
    根据故事 ID 和类型从 API 获取故事详情并处理文本内容。

    Args:
        story_id (str): 故事的唯一 ID。
        story_type (int, optional): 类型，默认为 2 (中文绘本)。
                                    1: 英文绘本, 2: 中文绘本。

    Returns:
        dict: 包含 storyId, storyLevel, storyName, text 的字典，
              如果出错则返回 None。
              text 是合并后的段落内容，跳过了与标题相同的首段。
    """
    api_url = f"{BASE_URL}/{story_type}/{story_id}"
    print(f"正在请求 URL: {api_url}")

    try:
        response = requests.get(api_url, timeout=10)  # 设置超时
        response.raise_for_status()  # 如果状态码不是 2xx，则抛出 HTTPError

        data = response.json()

        # 检查 API 返回的 code
        if data.get("code") != 200:
            print(f"API 返回错误: code={data.get('code')}, msg={data.get('msg')}")
            return None

        story_data = data.get("data")
        if not story_data or not isinstance(story_data, dict):
            print("API 返回的数据格式无效或 data 字段为空。")
            return None

        # 提取基本信息
        storyId = story_data.get("storyId")
        storyLevel = story_data.get("storyLevel")
        storyName = story_data.get("storyName", "").strip() # 获取并去除首尾空格
        paragraphs = story_data.get("paragraphs", [])

        if not storyId or storyLevel is None or not paragraphs:
            print("API 返回的数据缺少必要的字段 (storyId, storyLevel, paragraphs)。")
            return None

        # 按 sequenceOrder 排序段落
        paragraphs.sort(key=lambda p: p.get("sequenceOrder", float('inf')))

        # 合并文本，跳过与标题相同的首段
        merged_text_parts = []
        for p in paragraphs:
            seq_order = p.get("sequenceOrder")
            text = p.get("text", "").strip() # 获取并去除首尾空格

            # 如果是第一个段落 (sequenceOrder=0) 且内容与故事名相同，则跳过
            if seq_order == 0 and text == storyName:
                print(f"跳过与标题相同的段落 0: '{text}'")
                continue

            merged_text_parts.append(text)

        final_text = "".join(merged_text_parts)

        return {
            "storyId": storyId,
            "storyLevel": storyLevel,
            "storyName": storyName, # 返回处理过的 storyName
            "text": final_text,
        }

    except requests.exceptions.RequestException as e:
        print(f"请求 API 时发生错误: {e}")
        return None
    except json.JSONDecodeError:
        print("解析 API 响应 JSON 时发生错误。")
        return None
    except Exception as e:
        print(f"处理数据时发生未知错误: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="根据故事 ID 获取并处理故事内容。")
    parser.add_argument("story_id", type=str, help="要获取的故事的唯一 ID。")
    parser.add_argument(
        "--type",
        type=int,
        default=2,
        choices=[1, 2],
        help="故事类型 (1: 英文绘本, 2: 中文绘本)。默认为 2。",
    )

    args = parser.parse_args()

    story_details = get_story_details(args.story_id, args.type)

    if story_details:
        print("\n成功获取并处理故事详情:")
        # 使用 json.dumps 确保中文字符正确显示
        print(json.dumps(story_details, indent=4, ensure_ascii=False))
    else:
        print("\n无法获取或处理故事详情。")

    # 示例用法 (硬编码 ID)
    # print("\n--- 示例调用 ---")
    # example_id = "5e738a9dfea180771d9a9bfc" # 中文绘本 ID
    # example_type = 2
    # details = get_story_details(example_id, example_type)
    # if details:
    #     print(json.dumps(details, indent=4, ensure_ascii=False))
    # else:
    #     print(f"无法获取 ID 为 {example_id} 的故事详情。")
