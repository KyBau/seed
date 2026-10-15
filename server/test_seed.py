import json, os, subprocess, sys, tempfile, unittest
os.environ["SEED_HOME"] = tempfile.mkdtemp(); os.environ["SEED_MIN_INTERVAL"] = "0"
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
PIRATE = open(os.path.join(os.path.dirname(__file__), "fixtures", "a_pirate_i.txt")).read()
NEVSKY = "i don't pick traders anymore. i don't pick coins.\n\ngrok ranks the traders worth copying\nrugcheck kills the rugs before grok is even asked\ngrok calls COPY or SKIP on every buy\ncopyfomo fills it in ~1 sec, sells included\n\nfull setup, every file paste below"
class Regression(unittest.TestCase):
    def test_pirate_flags(self):
        f = " | ".join(S.flags_for({"text": PIRATE}))
        self.assertIn("BIG RETURN", f); self.assertIn("12.7x", f); self.assertIn("MULTIPLIER CLAIM: 12x", f)
        self.assertIn("88 wins + 37 losses = 125, not 97 trades", f); self.assertIn("70% hit rate vs 88/97", f)
    def test_variants(self):
        for txt in ["$1k -> $9,500", "$50 to $400 overnight", "TURNED $200 INTO $5K"]: self.assertTrue(any("BIG RETURN" in x for x in S.flags_for({"text": txt})), txt)
        self.assertEqual(S.flags_for({"text": "Bought 2 coins at $10 to $12 range"}), [])
        self.assertEqual(S.flags_for({"text": "10 trades, 6 wins, 4 losses"}), [])
    def test_queries(self):
        items = [{"text": PIRATE, "author": "@A_Pirate_I"}, {"text": NEVSKY, "author": "@0xNevsky"}]
        q = S.search_queries(items); j = " ".join(q)
        self.assertNotIn("min_faves", j); self.assertNotIn("them", j.split())
        self.assertTrue(any("copyfomo" in x and "grok" in x for x in q), q); self.assertIn("from:0xNevsky copyfomo", q); self.assertIn("from:A_Pirate_I copyfomo", q)
        for w in S.keywords([PIRATE, NEVSKY], 8): self.assertNotIn(w, S.STOP)
class Hunt(unittest.TestCase):
    def fake(self, calls):
        def ddg(q): calls.append(q); return [{"url": "https://x.com/c/status/3", "text": "copy trading wallets result", "source": "duckduckgo"},
                                            {"url": "https://blog.example/copytrade", "text": "Copy trading wallets guide: $100 into $5,000", "source": "duckduckgo"},
                                            {"url": "https://other.example/cats", "text": "cute cats", "source": "duckduckgo"}]
        def bad(q): raise PermissionError("SEED_X_BEARER not set")
        return {"x": bad, "duckduckgo": ddg}
    def test_hunt_post(self):
        calls = []; r = S.hunt("https://x.com/a/status/1", "hunt1", 1, 30, 10, searchers=self.fake(calls), fetch=lambda i: dict(FAKE[i]), art=lambda u: (u, "Guide", "score"))
        self.assertIn("duckduckgo", r["sources_ok"]); self.assertIn("x", r["sources_failed"])
        urls = [a["url"] for a in r["added"]]; self.assertIn("https://blog.example/copytrade", urls); self.assertNotIn("https://other.example/cats", urls)
        self.assertLessEqual(r["requests_used"], 30); self.assertTrue(r["summary"]); self.assertTrue(any("BIG RETURN" in f for f in r["flags"]))
    def test_budget(self):
        calls = []; r = S.hunt("copy trading wallets bot", "hunt2", 1, 5, 10, searchers=self.fake(calls))
        self.assertLessEqual(r["requests_used"], 5); self.assertEqual(r["topic"], "hunt2")
    def test_freetext_tool(self):
        S.SEARCHERS_BAK = S.SEARCHERS; S.SEARCHERS = self.fake([])
        try: self.assertFalse(call("seed_hunt", {"seed": "copy trading wallets", "topic": "hunt3", "budget": 10})["isError"])
        finally: S.SEARCHERS = S.SEARCHERS_BAK
    def test_ddg_parse(self):
        page = '<a rel="nofollow" class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fx.com%2Fg%2Fstatus%2F5&amp;rut=1">T <b>x</b></a><a class="result__snippet" href="#">snip</a>'
        orig = S._getj; S._getj = lambda u, h=None: page
        try: r = S.search_ddg("q")
        finally: S._getj = orig
        self.assertEqual(r[0]["url"], "https://x.com/g/status/5"); self.assertIn("snip", r[0]["text"])
@unittest.skipUnless(LIVE, "set SEED_LIVE=1 for network tests")
class Live(unittest.TestCase):
    def test_fxtwitter(self):
        r = call("seed_expand", {"post_url": "https://x.com/alucardiox/status/2110387861161656556", "topic": "live", "depth": 1, "max_items": 5})["structuredContent"]
        self.assertGreaterEqual(r["fetched"], 2, r)
    def test_hunt_live(self):
        r = call("seed_hunt", {"seed": "https://x.com/A_Pirate_I/status/2110761136706527452", "topic": "livehunt", "budget": 20})["structuredContent"]
        self.assertTrue({"bing", "duckduckgo"} & set(r["sources_ok"]), r); self.assertTrue(r["added"], r)
if __name__ == "__main__": unittest.main()
