"""Visitor IDs must not make an expired account pass login preflight."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from core.douyin_im import check_login, scrape_ssr


class SsrLoginTests(unittest.TestCase):
    @staticmethod
    def document(is_login=None, uid=None, missing_cookie=False):
        data = {
            "odin": json.dumps({"user_id": "10000000000000001"}),
            "not_exist_login_cookie": missing_cookie,
        }
        if is_login is not None:
            data["user"] = {"isLogin": is_login, "info": {"uid": uid or ""}}
        return json.dumps(data)

    def test_logged_out_visitor_id_does_not_pass_login(self):
        html = self.document(is_login=False)
        result = scrape_ssr(html)
        self.assertEqual(result["verdict"], "logged_out")
        self.assertIsNone(result["user_id"])
        page = Mock()
        page.content.return_value = html
        page.context.cookies.return_value = [{"name": "sessionid"}]
        login = check_login(page, SimpleNamespace(login=result))
        self.assertEqual(login["state"], "EXPIRED")

    def test_missing_login_cookie_overrides_visitor_id(self):
        self.assertEqual(scrape_ssr(self.document(missing_cookie=True))["verdict"],
                         "logged_out")

    def test_account_uid_takes_precedence_over_visitor_id(self):
        result = scrape_ssr(self.document(is_login=True, uid="10000000000000002"))
        self.assertEqual(result["verdict"], "logged_in")
        self.assertEqual(result["user_id"], "10000000000000002")

    def test_visitor_id_alone_is_not_evidence_of_login(self):
        self.assertEqual(scrape_ssr(self.document())["verdict"], "unknown")

    def test_explicit_login_can_use_odin_when_account_uid_absent(self):
        result = scrape_ssr(self.document(is_login=True))
        self.assertEqual(result["verdict"], "logged_in")
        self.assertEqual(result["user_id"], "10000000000000001")


if __name__ == "__main__":
    unittest.main()
