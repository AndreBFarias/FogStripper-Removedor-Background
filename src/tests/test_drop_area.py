from src.gui.constants import ALL_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS


def test_extensions_defined():
    assert len(IMAGE_EXTENSIONS) > 0
    assert len(VIDEO_EXTENSIONS) > 0
    assert len(ALL_EXTENSIONS) == len(IMAGE_EXTENSIONS) + len(VIDEO_EXTENSIONS)


def test_extensions_lowercase():
    for ext in ALL_EXTENSIONS:
        assert ext.startswith(".")
        assert ext == ext.lower()


def test_common_image_extensions():
    assert ".png" in IMAGE_EXTENSIONS
    assert ".jpg" in IMAGE_EXTENSIONS
    assert ".jpeg" in IMAGE_EXTENSIONS
    assert ".webp" in IMAGE_EXTENSIONS


def test_common_video_extensions():
    assert ".mp4" in VIDEO_EXTENSIONS
    assert ".gif" in VIDEO_EXTENSIONS
