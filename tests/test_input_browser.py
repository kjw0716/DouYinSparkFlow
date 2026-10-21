"""Real browser input regressions on an offline page; never contacts Douyin."""
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from urllib.parse import quote

from core.douyin_im import DouyinIM


class InputBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        binary = os.getenv("CLOAKBROWSER_BINARY_PATH", "")
        if not binary or not Path(binary).is_file():
            raise unittest.SkipTest("Set CLOAKBROWSER_BINARY_PATH for browser input tests")
        from cloakbrowser import launch
        cls.browser = launch(headless=True, humanize=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()

    def setUp(self):
        self.page = self.browser.new_page()
        html = '''<div class="messageEditorimChatEditorContainer">
          <div contenteditable="true" data-placeholder="发送消息" style="width:500px;height:100px"></div>
          </div><div id="messages"></div><script>
          window.sent = [];
          document.querySelector('[contenteditable]').addEventListener('keydown', e => {
            if (e.key !== 'Enter' || e.shiftKey) return;
            e.preventDefault();
            const text = e.target.innerText.trim();
            if (!text) return;
            window.sent.push(text);
            const box = document.createElement('div');
            box.className = 'MessageBoxContentisFromMe';
            const message = document.createElement('span');
            message.setAttribute('data-e2e', 'msg-item-content');
            message.textContent = text;
            box.appendChild(message);
            document.querySelector('#messages').appendChild(box);
            e.target.textContent = '';
          });</script>'''
        self.page.goto("data:text/html;charset=utf-8," + quote(html))
        self.im = object.__new__(DouyinIM)
        self.im.page = self.page
        self.im.mon = SimpleNamespace(sends=[])

    def tearDown(self):
        self.page.close()

    def test_mouse_move_probe_detects_working_input(self):
        self.assertEqual(self.im._input_mode(), "real")
        self.im._editor().click()
        self.page.keyboard.type("keyboard works")
        self.assertEqual(self.im._editor().inner_text(), "keyboard works")
        self.assertEqual(self.page.evaluate("window.sent"), [])

    def test_modern_editor_sends_once_with_dom_confirmation(self):
        text = "测试火花🔥"
        result = self.im.type_and_send({"conv_id": "offline", "display": "测试好友"}, text, timeout=4)
        self.assertEqual(result["delivery_state"], "confirmed")
        self.assertFalse(result["safe_to_retry"])
        self.assertEqual(self.page.evaluate("window.sent"), [text])
        self.assertEqual(self.im._editor().inner_text(), "")


if __name__ == "__main__":
    unittest.main()
