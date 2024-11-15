from unittest import mock

from django.test import TestCase

from core.services.utils import delete_temp_file


class UtilsTest(TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("os.remove")
    def test_delete_temp_file_exists(self, mock_remove, mock_isfile):
        mock_isfile.return_value = True
        result = delete_temp_file("fake_path/to/file.txt")
        mock_remove.assert_called_once_with("fake_path/to/file.txt")
        self.assertTrue(result)

    @mock.patch("os.path.isfile")
    @mock.patch("os.remove")
    def test_delete_temp_file_not_exists(self, mock_remove, mock_isfile):
        mock_isfile.return_value = False
        result = delete_temp_file("fake_path/to/non_existent_file.txt")
        mock_remove.assert_not_called()
        self.assertFalse(result)
