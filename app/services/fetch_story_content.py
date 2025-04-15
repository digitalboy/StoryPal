import requests
import logging
import json
import argparse
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 外部 API 基础 URL
EXTERNAL_API_BASE_URL = "http://106.52.130.188:8889"


def get_story_details(story_id: str, story_type: int = 2) -> Optional[Dict[str, Any]]:
    """
    从外部 API 获取指定 ID 和类型的故事详情。

    Args:
        story_id: 故事的唯一 ID。
        story_type: 故事类型 (默认为 2，表示中文绘本)。

    Returns:
        包含故事详情的字典 (storyName, text, storyLevel) 或在出错时返回 None。
    """
    list_url = (
        f"{EXTERNAL_API_BASE_URL}/content/getContentListById/{story_type}/{story_id}"
    )
    logger.info(f"Fetching story details from: {list_url}")

    try:
        response = requests.get(list_url, timeout=10)  # 设置超时

        # 检查 HTTP 响应状态码
        if response.status_code != 200:
            logger.error(
                f"Failed to fetch story {story_id}. Status code: {response.status_code}, Response: {response.text}"
            )
            return None

        # 解析 JSON 响应
        try:
            data = response.json()
            # 检查 API 返回的业务代码
            if data.get("code") != 200:
                logger.error(
                    f"API error for story {story_id}. Code: {data.get('code')}, Message: {data.get('msg')}"
                )
                return None

            # 直接获取 data 字段，预期是一个字典
            story_data = data.get("data")

            # 检查 story_data 是否存在且为字典
            if not story_data or not isinstance(story_data, dict):
                logger.error(
                    f"Invalid or missing 'data' field in API response for story {story_id} from {list_url}. Response: {data}"
                )
                return None

            # （可选但推荐）验证返回的 storyId 是否与请求的一致
            if story_data.get("storyId") != story_id:
                logger.warning(
                    f"Returned storyId '{story_data.get('storyId')}' does not match requested storyId '{story_id}' from {list_url}"
                )
                # 根据业务需求决定是否返回 None 或继续处理
                # return None

            # 提取并合并段落文本
            paragraphs = story_data.get("paragraphs", [])
            # 忽略 sequenceOrder 为 0 的标题段落
            story_text = " ".join(
                p.get("text", "") for p in paragraphs if p.get("sequenceOrder", -1) != 0
            ).strip()

            # 检查提取的数据是否有效
            story_name = story_data.get("storyName")
            story_level = story_data.get("storyLevel")

            if not story_name or not story_text or story_level is None:
                logger.warning(
                    f"Missing essential data (storyName, text, or storyLevel) in response for story {story_id}. Data: {story_data}"
                )
                # 根据业务需求决定是否返回 None
                # return None

            return {
                "storyName": story_name,
                "text": story_text,
                "storyLevel": story_level,
            }

        except json.JSONDecodeError:
            logger.exception(
                f"Failed to decode JSON response for story {story_id} from {list_url}"
            )
            return None
        except Exception as e:  # 捕获处理数据时可能出现的其他错误
            logger.exception(f"Error processing data for story {story_id}: {e}")
            return None

    except requests.exceptions.Timeout:
        logger.error(
            f"Request timed out when fetching story {story_id} from {list_url}"
        )
        return None
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request failed when fetching story {story_id}: {e}")
        return None
    except Exception as e:  # 捕获意料之外的错误
        logger.exception(
            f"An unexpected error occurred in get_story_details for story {story_id}: {e}"
        )
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
