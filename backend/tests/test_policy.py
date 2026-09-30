"""このマップが答えない質問（判断・今の状況）の判定の回帰テスト。

実行: backend/ で `python -m unittest discover tests`
"""

import unittest

from app.policy import detect_about_map, detect_out_of_scope


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


class DetectAboutMapTest(unittest.TestCase):
    def test_about_map(self):
        # このマップそのものについての質問。町丁目が決まっていなくてもDifyに渡す。
        for message in [
            "このマップは何？",
            "このマップはどうやって計算してるの？",
            "このツールの目的は？",
            "計算の方法を教えて",
            "試算の前提は？",
            "どうやって作ったの？",
            "チャットの仕組みは？",
            "使い方を教えて",
            "地図の見方が分からない",
            "紫色は何？",
            "使っている技術は？",
            "誰が作ったの？",
            "精度はどれくらい？",
            "流出係数って何？",
            "Difyを使ってる？",
            # 用語の意味を聞く質問
            "内水氾濫って何？",
            "内水はん濫とは",
            "暗渠って何？",
            "あんきょの意味は？",
            "立会川について教えて",
            "浸水想定区域とは何ですか",
            "アンダーパスって？",
            "床上浸水と床下浸水の違いは？",
        ]:
            with self.subTest(message=message):
                self.assertTrue(detect_about_map(message))

    def test_town_questions_pass(self):
        # 画面の質問例と、町丁目の事実を聞く質問は、このマップについての質問として扱わない。
        for message in [
            "中延六丁目について教えて",
            "水がたまりやすいのはどこ？",
            "土地の高さや地形は？",
            "過去にどれくらい浸水した？",
            "公式の浸水想定と試算はどう違う？",
            "近くの避難所と土のう置場は？",
            "土のうはどこでもらえる？",
            # 用語が入っていても、場所や町丁目ごとの事実を聞く質問
            "暗渠はどこを通ってる？",
            "立会川の近くは浸水しやすい？",
            "土のう置場はどこ？",
            "冠水しやすい道は？",
        ]:
            with self.subTest(message=message):
                self.assertFalse(detect_about_map(message))


if __name__ == "__main__":
    unittest.main()
