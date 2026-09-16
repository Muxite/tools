"""Tests for tcheck.py. Vendored from tundle ai4research/translate/checks; run with pytest"""

import tempfile
import unittest
from pathlib import Path

from tundlekit.translate import tcheck as t

ROWS = [
    {"en": "thread-safe|thread safety", "zh": "线程安全", "banned_en": "reentrant", "banned_zh": "可重入",
     "domain": "general", "status": "approved", "evidence": "", "note": ""},
    {"en": "reentrant", "zh": "可重入", "banned_en": "thread-safe", "banned_zh": "线程安全",
     "domain": "general", "status": "approved", "evidence": "", "note": ""},
    {"en": "process", "zh": "进程", "banned_en": "thread", "banned_zh": "线程",
     "domain": "general", "status": "approved", "evidence": "", "note": ""},
    {"en": "trust", "zh": "信任", "banned_en": "trust class", "banned_zh": "",
     "domain": "ai4research", "status": "approved", "evidence": "", "note": ""},
    {"en": "trust class", "zh": "信任等级", "banned_en": "trust level", "banned_zh": "",
     "domain": "ai4research", "status": "pending", "evidence": "", "note": ""},
    {"en": "side effect", "zh": "副作用", "banned_en": "effects", "banned_zh": "",
     "domain": "ai4research", "status": "approved", "evidence": "", "note": ""},
    {"en": "evidence", "zh": "证据", "banned_en": "proof", "banned_zh": "证明",
     "domain": "ai4research", "status": "approved", "evidence": "", "note": ""},
]


def tmp(text: str | bytes) -> str:
    f = tempfile.NamedTemporaryFile("wb", suffix=".md", delete=False)
    f.write(text.encode("utf-8") if isinstance(text, str) else text)
    f.close()
    return f.name


class Encoding(unittest.TestCase):
    MOJI = "真实任务".encode("utf-8").decode("cp1252", errors="replace")  # 'çœŸå®žä»»åŠ¡'-like

    def test_clean_chinese_passes(self):
        self.assertEqual(t.check_encoding(tmp("# 标题\n\n能力胶囊是自闭环的。\n")).fails, [])

    def test_real_mojibake_signature_fails_and_repairs(self):
        line = "# Phase 22 çœŸå®žä»»åŠ¡"
        self.assertTrue(t.check_encoding(tmp(line + "\n")).fails)
        fixed, n = t.repair_mojibake(line)
        self.assertEqual((fixed, n), ("# Phase 22 真实任务", 1))

    def test_undefined_cp1252_bytes_survive_as_c1_and_repair(self):
        # 状态 -> 'çŠ¶æ€\x81': 0x81 is undefined in CP1252 and survives as U+0081
        broken = "状态".encode("utf-8").decode("latin-1").replace("\x8a", "Š")
        self.assertTrue(t.MOJIBAKE.search(broken))
        self.assertEqual(t._unmojibake_line(broken), "状态")

    def test_mojibake_quoted_in_backticks_is_not_damage(self):
        doc = "The file opens with `ï»¿# Phase 22 çœŸå®ž...` (a CP1252 roundtrip).\n"
        self.assertEqual(t.check_encoding(tmp(doc)).fails, [])

    def test_replacement_char_and_invalid_utf8(self):
        self.assertTrue(t.check_encoding(tmp("丢失了 � 字节\n")).fails)
        self.assertTrue(t.check_encoding(tmp("中文".encode("gb18030"))).fails)

    def test_french_accents_are_not_mojibake(self):
        self.assertEqual(t.check_encoding(tmp("café, résumé, déjà vu, naïve\n")).fails, [])

    def test_repair_leaves_clean_lines_alone(self):
        text = "正常的一行\nçœŸå®ž\n"
        fixed, n = t.repair_mojibake(text)
        self.assertEqual((fixed, n), ("正常的一行\n真实\n", 1))


class Spans(unittest.TestCase):
    SRC = ("配置 `retry_limit` 为 3，详见 https://example.com/docs。\n\n"
           "```yaml\nretry_limit: 3  # 重试次数\n```\n\n文件在 harness/lib/gate_ledger.py 中。\n")
    GOOD = ("Set `retry_limit` to 3; see https://example.com/docs.\n\n"
            "```yaml\nretry_limit: 3  # 重试次数\n```\n\n*Translated comments:*\n- line 1 `# 重试次数` → retry count\n\n"
            "The file is in harness/lib/gate_ledger.py.\n")

    def test_faithful_passes(self):
        r = t.check_spans(self.SRC, self.GOOD, direction="zh-en")
        self.assertEqual(r.fails, [])
        self.assertEqual(r.warns, [])

    def test_url_followed_by_chinese_full_stop(self):
        self.assertIn("https://example.com/docs", t.extract_spans(self.SRC)["URL"])

    def test_digit_adjacent_to_cjk_is_extracted(self):
        # Python's \w matches CJK; the checker must still see the 3 in 第3步
        self.assertIn("3", t.extract_spans("执行第3步，共5步。")["number"])

    def test_comment_translated_inside_block_fails(self):
        bad = self.GOOD.replace("3  # 重试次数\n```", "3  # retry count\n```")
        self.assertTrue(t.check_spans(self.SRC, bad).fails)

    def test_url_directly_followed_by_chinese(self):
        self.assertIn("https://example.com/docs", t.extract_spans("见 https://example.com/docs中的说明")["URL"])

    def test_chinese_heading_anchor_is_protected(self):
        r = t.check_spans("见[定义](#胶囊定义)。", "See [the definition](#capsule-definition).")
        self.assertTrue(any("link target" in f for f in r.fails))

    def test_parenthesised_chinese_sentence_still_counts_as_untranslated(self):
        tgt = "After the node (节点完成后触发验收) (失败时回滚)."
        self.assertGreater(t.untranslated_ratio(tgt), 0.05)

    def test_changed_inline_code_fails(self):
        bad = self.GOOD.replace("`retry_limit`", "`retryLimit`")
        self.assertTrue(any("inline code missing" in f for f in t.check_spans(self.SRC, bad).fails))

    def test_added_backticks_only_warn(self):
        r = t.check_spans("调用 run 函数。", "Call the `run` function.")
        self.assertEqual(r.fails, [])
        self.assertTrue(any("added" in w for w in r.warns))

    def test_copying_the_source_fails_as_untranslated(self):
        self.assertTrue(any("Chinese" in f for f in t.check_spans(self.SRC, self.SRC, direction="zh-en").fails))

    def test_glossed_terms_and_tns_do_not_trip_untranslated(self):
        tgt = "A capsule (胶囊) is a self-contained closed loop (自闭环) [TN: 自闭环 is pending]. " * 3
        self.assertEqual(t.check_spans("胶囊是自闭环。", tgt, direction="zh-en").fails, [])

    def test_unbalanced_fence_from_line_range_warns(self):
        r = t.check_spans("说明\n```yaml\na: 1\n", "Note\n```yaml\na: 1\n")
        self.assertTrue(any("unbalanced" in w for w in r.warns))

    def test_nested_fence_longer_marker(self):
        doc = "````md\n```yaml\na: 1\n```\n````\n"
        self.assertEqual(len(t.extract_spans(doc)["code block"]), 1)

    def test_and_or_is_not_a_path(self):
        self.assertEqual(t.extract_spans("read and/or write, Skill/MCP/Agent")["path"], {})


class Glossary(unittest.TestCase):
    def test_banned_rendering_fails(self):
        r = t.check_glossary("该函数是可重入的。", "The function is thread-safe.", "zh-en", ROWS)
        self.assertTrue(r.fails)

    def test_both_terms_in_source_downgrades_to_warning(self):
        r = t.check_glossary("它是线程安全的，但不可重入。", "It is thread-safe but not reentrant.", "zh-en", ROWS)
        self.assertEqual(r.fails, [])

    AUTH = [{"en": "authentication|authenticate", "zh": "认证", "banned_en": "authorization|authorize",
             "banned_zh": "授权", "domain": "general", "status": "approved", "evidence": "", "note": ""}]

    def test_banned_inflected_form_fails(self):
        r = t.check_glossary("用户需先认证。", "The user must first be authorized.", "zh-en", self.AUTH)
        self.assertTrue(r.fails)

    def test_banned_alongside_approved_only_warns(self):
        r = t.check_glossary("表单认证", "Authentication of the form; authorization is separate.", "zh-en", self.AUTH)
        self.assertEqual(r.fails, [])
        self.assertTrue(r.warns)

    def test_multiword_ban_containing_approved_rendering_fires(self):
        r = t.check_glossary("每个胶囊都有信任。", "Each capsule has a trust class.", "zh-en", ROWS)
        self.assertTrue(r.fails)

    def test_pending_row_cannot_switch_off_approved_row(self):
        rows = ROWS + [{"en": "thread-safe", "zh": "可重入的", "banned_en": "", "banned_zh": "",
                        "domain": "general", "status": "pending", "evidence": "", "note": ""}]
        r = t.check_glossary("该函数是可重入的。", "The function is thread-safe.", "zh-en", rows)
        # it may shadow the approved row, but never silently
        self.assertTrue(r.fails or any("not enforced here" in w for w in r.warns))

    def test_domain_selection(self):
        self.assertEqual({r["domain"] for r in t.select_domains(ROWS, "general")}, {"general"})

    def test_tie_order_is_deterministic(self):
        self.assertEqual(t._longest_first(["并发", "发布", "合并"]), ["发布", "合并", "并发"])

    def test_longest_source_match_wins(self):
        # 信任等级 must not also trigger the 信任 row (whose ban is "trust class")
        r = t.check_glossary("每个胶囊有一个信任等级。", "Each capsule has a trust class.", "zh-en", ROWS)
        self.assertEqual(r.fails, [])
        self.assertTrue(any("pending" in i for i in r.infos))
        self.assertTrue(any("not enforced here" in w for w in r.warns))

    def test_banned_word_inside_approved_rendering_is_masked(self):
        r = t.check_glossary("记录副作用。", "Record side effects.", "zh-en", ROWS)
        self.assertEqual(r.fails, [])

    def test_banned_word_outside_approved_rendering_still_fails(self):
        r = t.check_glossary("记录副作用。", "Record the effects.", "zh-en", ROWS)
        self.assertTrue(r.fails)

    def test_evidence_strengthened_to_proof_fails(self):
        r = t.check_glossary("这是验收证据。", "This is acceptance proof.", "zh-en", ROWS)
        self.assertTrue(r.fails)

    def test_tn_naming_the_term_overrides_and_is_reported(self):
        tgt = "In the course of development [TN: 进程 here means course of events, not an OS process], the thread..."
        r = t.check_glossary("在开发进程中，线程……", tgt, "zh-en", ROWS)
        self.assertTrue(any("overridden" in i for i in r.infos))
        self.assertFalse(any("进程" in f for f in r.fails))

    def test_tn_not_naming_the_term_does_not_override(self):
        r = t.check_glossary("该函数是可重入的。", "The function is thread-safe [TN: see docs].", "zh-en", ROWS)
        self.assertTrue(r.fails)

    def test_missing_approved_rendering_only_warns(self):
        r = t.check_glossary("这是证据。", "This is support.", "zh-en", ROWS)
        self.assertEqual(r.fails, [])
        self.assertTrue(r.warns)

    def test_inflections(self):
        self.assertTrue(t.term_in("processes were started", "process", True))
        self.assertTrue(t.term_in("it was reentered", "reenter", True, loose=True))
        self.assertFalse(t.term_in("processing", "process", True))
        self.assertTrue(t.term_in("thread-safe code", "thread", True))  # hyphen is a boundary

    def test_en_zh_direction(self):
        r = t.check_glossary("The handler is reentrant.", "该处理器是线程安全的。", "en-zh", ROWS)
        self.assertTrue(r.fails)

    def test_bold_initial_letter_does_not_hide_term(self):
        rows = [{**ROWS[6], "en": "safety", "zh": "安全性", "banned_en": ""}]
        r = t.check_glossary("**S**afety - 安全性可验证", "**S**afety: verifiable", "zh-en", rows)
        self.assertEqual(r.warns, [])

    def test_code_and_inline_code_are_not_term_matched(self):
        r = t.check_glossary("字段 `可重入` 保持不变。", "The field `可重入` is unchanged; thread-safe.", "zh-en", ROWS)
        self.assertEqual(r.fails, [])


class ShippedGlossary(unittest.TestCase):
    def test_shipped_glossary_is_well_formed_and_conflict_free(self):
        rows, problems = t.load_glossary()
        self.assertEqual(problems, [])
        self.assertGreater(len(rows), 50)

    def test_conflicting_approved_rows_are_detected(self):
        path = tmp("en\tzh\tbanned_en\tbanned_zh\tdomain\tstatus\tevidence\tnote\n"
                   "release\t发布\t\t\tgeneral\tapproved\t\t\n"
                   "publish\t发布\t\t\tgeneral\tapproved\t\t\n"
                   "bad\trow\n")
        _, problems = t.load_glossary(Path(path))
        self.assertTrue(any("conflict" in p for p in problems))
        self.assertTrue(any("column count" in p for p in problems))


class ReadText(unittest.TestCase):
    def test_crlf_and_multiple_translation_blocks(self):
        path = tmp("<translation>\r\nOne\r\n</translation>\r\nnotes\r\n<translation>\r\nTwo\r\n</translation>\r\n")
        self.assertEqual(t.read_text(path), "One\n\nTwo")

    def test_line_range_and_translation_block(self):
        path = tmp("a\nb\nc\nd\n")
        self.assertEqual(t.read_text(f"{path}:2-3"), "b\nc\n")
        wrapped = tmp("<translation>\nHello\n</translation>\n\n## Translator notes\n- none\n")
        self.assertEqual(t.read_text(wrapped), "Hello")


if __name__ == "__main__":
    unittest.main()
