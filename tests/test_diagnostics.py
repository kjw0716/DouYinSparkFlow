"""Scheduled runs retain login/friend-list evidence without affecting delivery."""
import unittest
from unittest.mock import Mock, patch

from core import tasks
from core.diagnostics import capture_page


class PageCaptureTests(unittest.TestCase):
    def test_capture_is_disabled_by_default(self):
        page = Mock()
        with patch.dict("os.environ", {}, clear=True):
            capture_page(page, "test", "ready", Mock())
        page.screenshot.assert_not_called()

    def test_screenshot_failure_does_not_break_task(self):
        page = Mock()
        page.url = "https://www.douyin.com/chat"
        page.screenshot.side_effect = RuntimeError("closed page")
        logger = Mock()
        with patch.dict("os.environ", {"DOUYIN_CAPTURE_PAGES": "1"}), \
             patch("core.diagnostics.Path.mkdir"), \
             patch("core.diagnostics.Path.write_text"):
            capture_page(page, "test", "ready", logger)
        logger.warning.assert_called_once()

    def test_expired_login_is_captured_before_context_closes(self):
        browser = Mock()
        context = browser.new_context.return_value
        im = Mock()
        im.ready = False
        im.wait_ready.return_value = {"status": "EXPIRED"}
        with patch.object(tasks, "DouyinIM", return_value=im), \
             patch.object(tasks, "capture_page") as capture:
            capture.side_effect = lambda *args: context.close.assert_not_called()
            result = tasks.do_user_task(browser, "test", [], [])
        self.assertFalse(result["ok"])
        self.assertEqual(capture.call_args.args[2], "login_check_failed")
        im.iter_find_and_select.assert_not_called()
        context.close.assert_called_once()

    def test_ready_list_is_captured_before_friend_scan(self):
        browser = Mock()
        im = Mock()
        im.ready = True
        im.wait_ready.return_value = {"status": "READY"}
        im.last_scan = {}
        im.fold_groups.return_value = {}
        with patch.object(tasks, "DouyinIM", return_value=im), \
             patch.object(tasks, "capture_page") as capture:
            def scan(targets):
                self.assertEqual(capture.call_args.args[2], "friends_list_ready")
                return iter(())
            im.iter_find_and_select.side_effect = scan
            tasks.do_user_task(browser, "test", [], [])

    def test_unexpected_error_is_captured_and_propagated(self):
        browser = Mock()
        with patch.object(tasks, "DouyinIM", side_effect=RuntimeError("navigation")), \
             patch.object(tasks, "capture_page") as capture:
            with self.assertRaisesRegex(RuntimeError, "navigation"):
                tasks.do_user_task(browser, "test", [], [])
        self.assertEqual(capture.call_args.args[2], "task_exception")
        browser.new_context.return_value.close.assert_called_once()
