"""Тесты для патчей."""
import sys
from unittest import (
    TestCase,
)
from unittest.case import (
    skipUnless,
)

from educommon.utils.patches import (
    patch_utf8_assertion_error,
)


@skipUnless(sys.version_info.major == 2, 'Python 2 only')
class AssertionErrorUtf8PatchTestCase(TestCase):
    """Проверка патча AssertionError, позволяющего использовать кириллицу."""

    @classmethod
    def setUpClass(cls):
        """Патчит AssertionError."""
        cls._old_assertion_error = __builtins__['AssertionError']
        patch_utf8_assertion_error()

    @classmethod
    def tearDownClass(cls):
        """Возвращает оригинальный AssertionError."""
        __builtins__['AssertionError'] = cls._old_assertion_error

    def test_ascii(self):
        """Проверяет, что ascii сообщения выводятся корректно."""
        with self.assertRaises(AssertionError) as context:
            raise AssertionError('Exception')
        self.assertEqual(context.exception.message, 'Exception')

    def test_unicode(self):
        """Проверяет, что unicode сообщения конвертируются в utf-8."""
        with self.assertRaises(AssertionError) as context:
            raise AssertionError('Исключение')
        self.assertEqual(
            context.exception.message,
            'Исключение'.encode('utf-8')
        )

    def test_repeatable_patch(self):
        """Проверяет, что повторный вызов игнорируется."""
        self.assertIs(AssertionError.__base__, self._old_assertion_error)
        patch_utf8_assertion_error()
        self.assertIs(AssertionError.__base__, self._old_assertion_error)
