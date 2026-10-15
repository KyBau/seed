import json, os, subprocess, sys, tempfile, unittest
os.environ["SEED_HOME"] = tempfile.mkdtemp()
sys.path.insert(0, os.path.dirname(__file__)); import seed_server as S
LIVE = os.environ.get("SEED_LIVE", "0") == "1"
def call(n, a): return S.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": n, "arguments": a}})["result"]
FAKE = {
 "1": {"url": "https://x.com/a/status/1", "id": "1", "text": "Bot trading setup: score each market 0 to 1, skip below 0.50. $61 to $8,947 in 24 hours", "author": "@a", "quote": "https://x.com/b/status/2", "parent": None, "links": ["https://example.com/guide"]},
 "2": {"url": "https://x.com/b/status/2", "id": "2", "text": "Full guide to bot trading setup: score markets, backtest cutoff weekly. QuantGPT $81/month", "author": "@b", "quote": None, "parent": "3", "links": []},
 "3": {"url": "https://x.com/c/status/3", "id": "3", "text": "Copy trading wallets: 97 trades, 88 wins, 37 losses", "author": "@c", "quote": None, "parent": None, "links": []},
}
class Protocol(unittest.TestCase):
    def test_init(self):
        r = S.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})["result"]
        self.assertEqual(r["serverInfo"]["name"], "seed"); self.assertEqual(r["protocolVersion"], "2025-06-18")
    def test_tools(self):
        t = S.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertIn("seed_expand", {x["name"] for x in t})
        for x in t: self.assertFalse(x["annotations"]["destructiveHint"]); self.assertLessEqual(len(x["name"]), 64)
    def test_unknown(self): self.assertIn("error", S.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "post_tweet"}}))
    def test_notification(self): self.assertIsNone(S.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))
    def test_bad_url(self): self.assertTrue(call("seed_expand", {"post_url": "https://example.com"})["isError"])
    def test_stdio(self):
        out = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "seed_server.py")], input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n', capture_output=True, text=True, timeout=10).stdout
        self.assertEqual(len(json.loads(out)["result"]["tools"]), len(S.TOOLS))
class Pipeline(unittest.TestCase):
    def test_flow(self):
        r = S.expand("https://x.com/a/status/1", "trading", 2, 40, fetch=lambda i: dict(FAKE[i]), art=lambda u: (u, "Guide title", "score markets"))
        self.assertEqual(r["fetched"], 4); self.assertEqual({i["kind"] for i in r["items"]}, {"seed", "quote", "parent", "article"}); self.assertTrue(r["search_queries"])
        d = call("seed_distill", {"topic": "trading"})["structuredContent"]
        fl = [f for c in d["clusters"] for f in c["flags"]]
        self.assertTrue(any("BIG RETURN" in f for f in fl)); self.assertTrue(any("ADD UP" in f for f in fl)); self.assertTrue(any("PROMOTIONAL" in f for f in fl))
        b = call("seed_blueprint", {"topic": "trading"})["structuredContent"]
        self.assertGreaterEqual(len(b["prebuild_questions"]), 5); self.assertTrue(all(q["options"] for q in b["prebuild_questions"]))
        self.assertTrue(call("seed_add", {"topic": "trading", "url": "https://x.com/d/status/9", "text": "new idea"})["structuredContent"]["added"])
        self.assertFalse(call("seed_add", {"topic": "trading", "url": "https://x.com/d/status/9", "text": "dup"})["structuredContent"]["added"])
        self.assertEqual(len(call("seed_digest", {"topic": "trading"})["structuredContent"]["new_items"]), 5)
        self.assertIn("trading", [t["topic"] for t in call("seed_topics", {})["structuredContent"]["topics"]])
    def test_depth_zero(self):
        r = S.expand("https://x.com/a/status/1", "d0", 0, 40, fetch=lambda i: dict(FAKE[i]), art=lambda u: (u, "", ""))
        self.assertEqual(r["fetched"], 1)
    def test_empty_distill(self): self.assertTrue(call("seed_distill", {"topic": "nothing"})["isError"])
@unittest.skipUnless(LIVE, "set SEED_LIVE=1 for network tests")
class Live(unittest.TestCase):
    def test_fxtwitter(self):
        r = call("seed_expand", {"post_url": "https://x.com/alucardiox/status/2110387861161656556", "topic": "live", "depth": 1, "max_items": 5})["structuredContent"]
        self.assertGreaterEqual(r["fetched"], 2, r)
if __name__ == "__main__": unittest.main()
