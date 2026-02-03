from prl.io import read_text_any


def test_read_text_any_shift_jis(tmp_path):
    content = "こんにちは"
    path = tmp_path / "sample.txt"
    path.write_bytes(content.encode("shift_jis"))
    assert read_text_any(path) == content
