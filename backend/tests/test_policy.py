"""このマップが答えない質問（判断・今の状況）の判定の回帰テスト。

実行: backend/ で `python -m unittest discover tests`
"""

import unittest

from app.policy import detect_out_of_scope


class DetectOutOfScopeTest(unittest.TestCase):
    def test_judgment(self):
        for message in [
            "避難したほうがいい？",
            "避難すべきですか",
            "この道は通れる？",
            "うちは安全ですか？",
            "どこに逃げればいい？",
            "避難経路を教えて",
            "いまの雨は大丈夫？",
        ]:
            with self.subTest(message=message):
                self.assertEqual(detect_out_of_scope(message), "judgment")

    def test_realtime(self):
        for message in [
            "今、中延六丁目は浸水してる？",
            "明日の大雨で二葉二丁目は浸水する？",
            "避難所は開いてる？",
            "源氏前小学校は今開設されてる？",
            "大雨警報は出てる？",
            "現在の雨量は？",
        ]:
            with self.subTest(message=message):
                self.assertEqual(detect_out_of_scope(message), "realtime")

    def test_answerable_questions_pass(self):
        # 画面の質問例（ChatPanel.jsx の FOLLOW_UP_QUESTIONS）と、備え・過去・一般の質問は止めない。
        for message in [
            "中延六丁目について教えて",
            "二葉二丁目で水がたまりやすいのはどこ？",
            "二葉二丁目の土地の高さや地形は？",
            "二葉二丁目は過去にどれくらい浸水した？",
            "二葉二丁目の公式の浸水想定と試算はどう違う？",
            "二葉二丁目の近くの避難所と土のう置場は？",
            "今までに浸水したことはある？",
            "今回の試算の前提は？",
            "今のうちに備えておくことは？",
            "明日からできる備えは？",
            "土のうはどこでもらえる？",
            "避難所はどこ？",
            "内水氾濫って何？",
        ]:
            with self.subTest(message=message):
                self.assertIsNone(detect_out_of_scope(message))


if __name__ == "__main__":
    unittest.main()
