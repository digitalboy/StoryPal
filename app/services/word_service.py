# app/services/word_service.py
import json
import logging
from app.config import Config
from app.models.word_model import WordModel


class WordService:
    def __init__(self):
        self.words = self._load_words()

    def _load_words(self):
        logging.info("Loading words data from json file")
        try:
            with open(Config.WORDS_FILE_PATH, "r", encoding="utf-8") as f:
                words_data = json.load(f)
            logging.info(f"Loaded {len(words_data)} words from file")
            return {
                word_data["word_id"]: WordModel.from_dict(word_data)
                for word_data in words_data
            }
        except FileNotFoundError:
            logging.error("words.json not found")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding json file: {e}")
            return {}

    def get_word(self, word_id):
        logging.info(f"Getting word by id: {word_id}")
        return self.words.get(word_id)

    def list_words(self, level=None, part_of_speech=None, page=1, page_size=10):
        logging.info(
            f"Listing words, level: {level}, part_of_speech: {part_of_speech}, page: {page}, page_size: {page_size}"
        )
        filtered_words = list(self.words.values())

        if level:
            filtered_words = [
                word for word in filtered_words if word.chaotong_level <= level
            ]
        if part_of_speech:
            filtered_words = [
                word for word in filtered_words if word.part_of_speech == part_of_speech
            ]

        start = (page - 1) * page_size
        end = start + page_size
        return filtered_words[start:end]

    def add_word(self, word_data):
        logging.info(f"Adding word {word_data}")
        word = WordModel.from_dict(word_data)
        self.words[word.word_id] = word
        return word

    def update_word(self, word_id, word_data):
        logging.info(f"Updating word {word_id} with {word_data}")
        word = self.get_word(word_id)
        if not word:
            logging.error(f"Word not found {word_id}")
            return None
        updated_word = WordModel(word_id=word_id, **word_data)
        self.words[word_id] = updated_word
        return updated_word

    def delete_word(self, word_id):
        logging.info(f"Deleting word {word_id}")
        word = self.get_word(word_id)
        if not word:
            logging.error(f"Word not found {word_id}")
            return None
        del self.words[word_id]
        return word
