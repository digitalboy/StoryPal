# filepath: tests/test_words.py
import pytest
from app import create_app
import json
from app.models.word_model import Word


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


def clear_json_file(filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([], f)


@pytest.fixture(scope="function", autouse=True)
def setup_teardown():
    clear_json_file("data/words.json")
    yield


def test_create_word(client):
    """测试创建字词 API"""
    data = {
        "word": "你好",
        "pinyin": "nǐ hǎo",
        "definition": "hello",
        "part_of_speech": "代词",
        "chaotong_level": 1,
    }
    response = client.post("/v1/words", json=data)
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert "word_id" in response.json["data"]
    word_id = response.json["data"]["word_id"]
    word = Word.find_by_id(word_id)
    assert word
    assert word.word == "你好"


def test_create_word_missing_required_fields(client):
    """测试创建字词 API，缺少必填字段"""
    data = {
        "pinyin": "nǐ hǎo",
        "definition": "hello",
        "part_of_speech": "代词",
        "chaotong_level": 1,
    }
    response = client.post("/v1/words", json=data)
    assert response.status_code == 400
    assert response.json["code"] == 4001
    assert response.json["message"] == "缺少必填字段: word"


def test_get_word(client):
    """测试获取字词 API"""
    data = {
        "word": "你好",
        "pinyin": "nǐ hǎo",
        "definition": "hello",
        "part_of_speech": "代词",
        "chaotong_level": 1,
    }
    response = client.post("/v1/words", json=data)
    word_id = response.json["data"]["word_id"]
    response = client.get(f"/v1/words/{word_id}")
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert response.json["data"]["word"] == "你好"


def test_get_word_not_found(client):
    """测试获取字词 API，字词不存在"""
    response = client.get("/v1/words/non_existent_id")
    assert response.status_code == 404
    assert response.json["code"] == 4042
    assert response.json["message"] == "Word not found"


def test_update_word(client):
    """测试更新字词 API"""
    data = {
        "word": "你好",
        "pinyin": "nǐ hǎo",
        "definition": "hello",
        "part_of_speech": "代词",
        "chaotong_level": 1,
    }
    response = client.post("/v1/words", json=data)
    word_id = response.json["data"]["word_id"]
    update_data = {"word": "您好", "definition": "hello(polite)"}
    response = client.put(f"/v1/words/{word_id}", json=update_data)
    assert response.status_code == 200
    assert response.json["code"] == 200
    response = client.get(f"/v1/words/{word_id}")
    assert response.json["data"]["word"] == "您好"
    assert response.json["data"]["definition"] == "hello(polite)"


def test_update_word_not_found(client):
    """测试更新字词 API，字词不存在"""
    update_data = {"word": "您好", "definition": "hello(polite)"}
    response = client.put("/v1/words/non_existent_id", json=update_data)
    assert response.status_code == 404
    assert response.json["code"] == 4042
    assert response.json["message"] == "Word not found"


def test_delete_word(client):
    """测试删除字词 API"""
    data = {
        "word": "你好",
        "pinyin": "nǐ hǎo",
        "definition": "hello",
        "part_of_speech": "代词",
        "chaotong_level": 1,
    }
    response = client.post("/v1/words", json=data)
    word_id = response.json["data"]["word_id"]
    response = client.delete(f"/v1/words/{word_id}")
    assert response.status_code == 200
    assert response.json["code"] == 200
    response = client.get(f"/v1/words/{word_id}")
    assert response.status_code == 404


def test_delete_word_not_found(client):
    """测试删除字词 API，字词不存在"""
    response = client.delete("/v1/words/non_existent_id")
    assert response.status_code == 404
    assert response.json["code"] == 4042
    assert response.json["message"] == "Word not found"


def test_get_words_by_level(client):
    """测试按等级查询字词 API"""
    data1 = {
        "word": "你好",
        "pinyin": "nǐ hǎo",
        "definition": "hello",
        "part_of_speech": "代词",
        "chaotong_level": 1,
    }
    data2 = {
        "word": "早上好",
        "pinyin": "zǎo shang hǎo",
        "definition": "good morning",
        "part_of_speech": "代词",
        "chaotong_level": 2,
    }
    client.post("/v1/words", json=data1)
    client.post("/v1/words", json=data2)
    response = client.get("/v1/words?level=1")
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert len(response.json["data"]["words"]) == 1
    assert response.json["data"]["words"][0]["word"] == "你好"


def test_get_words_by_part_of_speech(client):
    """测试按词性查询字词 API"""
    data1 = {
        "word": "你好",
        "pinyin": "nǐ hǎo",
        "definition": "hello",
        "part_of_speech": "代词",
        "chaotong_level": 1,
    }
    data2 = {
        "word": "跑步",
        "pinyin": "pǎo bù",
        "definition": "run",
        "part_of_speech": "动词",
        "chaotong_level": 2,
    }
    client.post("/v1/words", json=data1)
    client.post("/v1/words", json=data2)
    response = client.get("/v1/words?part_of_speech=动词")
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert len(response.json["data"]["words"]) == 1
    assert response.json["data"]["words"][0]["word"] == "跑步"


def test_get_words_with_pagination(client):
    """测试带分页的查询字词 API"""
    for i in range(25):
        data = {
            "word": f"词语{i}",
            "pinyin": f"ciyu{i}",
            "definition": f"definition{i}",
            "part_of_speech": "名词",
            "chaotong_level": 1,
        }
        client.post("/v1/words", json=data)

    response = client.get("/v1/words?page=2&page_size=10")
    assert response.status_code == 200
    assert response.json["code"] == 200
    assert len(response.json["data"]["words"]) == 10
    assert response.json["data"]["total"] == 25
    assert response.json["data"]["words"][0]["word"] == "词语10"
