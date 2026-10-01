import json, sys
from collections import Counter
d = json.load(open(sys.argv[1], encoding="utf-8"))
V = [v for v in d["violations"] if v["severity"] == "error"]
U = d.get("unconnected_items", [])
print("%s DRC errors: %d %s | unconnected: %d" % (sys.argv[2], len(V), dict(Counter(v["type"] for v in V)), len(U)))
for v in V[:12]:
    print("-", v["type"], "::", " | ".join(i.get("description", "") for i in v["items"])[:150], "@", v["items"][0].get("pos"))
for u in U[:6]:
    print("U", " | ".join(i.get("description", "") for i in u["items"])[:150], [i.get("pos") for i in u["items"]])
if sys.argv[2] == "final":
    open("drc_ok.flag", "w").write("1" if (not V and not U) else "0")
