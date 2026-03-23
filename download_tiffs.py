import requests
import os
from time import sleep

# === YOUR EXAMPLE TIFF (the one you just sent) ===
url = "https://d3b30j659x3uym.cloudfront.net/2026/0318/202600768872.tif?v=639098917452366852&Expires=1774312945&Signature=OosTDDbOol90FbpofiBil2QUSZJVGKgAfG53eLqBa-as5WpnZIaojYjGuD4VAbhWF7FZn4Aomhu4SqgLa4k0ipZ01~oaezvPztQgD4TCVISEdRMjiMcr8P7cdntf2COoafEa9PbBHDiJDDRBsHkCEAgfqE~HmpDougmu3Ixx8f9dT9BALwSEOY2V0gVufbE-Fw7~QQV0CE~HnL6NjfBUQJvloLOQ6r3~TOsnrDucAM0HP0ThTvbzzTXJtEpOk9nam2ZLLBShjeyrlaYlUcQTL0ya6~KHfNnN~2wHmntmChl-45JyfS4J1rq01oBggIyoxYUtJI~xsNEGnlyPIrEnLg__&Key-Pair-Id=APKA2S2656W234S2XMMF"

filename = "202600768872.tif"
save_path = os.path.join("tiffs", filename)

print(f"📥 Downloading {filename} ... (this saves it forever)")

response = requests.get(url, stream=True)
response.raise_for_status()

with open(save_path, "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"✅ SUCCESS! Saved permanently here:")
print(f"   {save_path}")
print(f"   File size: {os.path.getsize(save_path) / 1024:.1f} KB")
print("\nYou can now open it in Preview to check it worked!")