import pytest

from src.core.constants import ALL_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS


class TestConstants:
    def test_video_extensions_is_tuple(self) -> None:
        assert isinstance(VIDEO_EXTENSIONS, tuple)

    def test_image_extensions_is_tuple(self) -> None:
        assert isinstance(IMAGE_EXTENSIONS, tuple)

    def test_all_extensions_is_tuple(self) -> None:
        assert isinstance(ALL_EXTENSIONS, tuple)

    def test_video_extensions_contains_common_formats(self) -> None:
        assert ".mp4" in VIDEO_EXTENSIONS
        assert ".gif" in VIDEO_EXTENSIONS
        assert ".webm" in VIDEO_EXTENSIONS

    def test_image_extensions_contains_common_formats(self) -> None:
        assert ".png" in IMAGE_EXTENSIONS
        assert ".jpg" in IMAGE_EXTENSIONS
        assert ".webp" in IMAGE_EXTENSIONS

    def test_all_extensions_combines_both(self) -> None:
        assert len(ALL_EXTENSIONS) == len(IMAGE_EXTENSIONS) + len(VIDEO_EXTENSIONS)
        for ext in IMAGE_EXTENSIONS:
            assert ext in ALL_EXTENSIONS
        for ext in VIDEO_EXTENSIONS:
            assert ext in ALL_EXTENSIONS

    def test_extensions_are_lowercase_with_dot(self) -> None:
        for ext in ALL_EXTENSIONS:
            assert ext.startswith(".")
            assert ext == ext.lower()
