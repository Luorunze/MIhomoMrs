import json
import os
import subprocess
import sys
import urllib.request

CONFIG_FILE = "rules.json"
OUTPUT_DIR = "dist"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        rules = json.load(f)

    has_error = False

    for item in rules:
        name = item["name"]
        behavior = item["behavior"]  # domain 或 ipcidr
        fmt = item["format"]        # yaml 或 text
        url = item["url"]

        temp_src = os.path.join(OUTPUT_DIR, f"temp_{name}_{fmt}")
        output_mrs = os.path.join(OUTPUT_DIR, name)

        print(f"[*] 正在下载: {name} <- {url}")
        try:
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "Mozilla/5.0 (compatible; RulesetConverter/1.0)"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp, open(temp_src, "wb") as out_file:
                out_file.write(resp.read())

            print(f"[*] 正在转换: {name} (类型: {behavior}, 格式: {fmt})")
            cmd = ["mihomo", "convert-ruleset", behavior, fmt, temp_src, output_mrs]
            subprocess.run(cmd, check=True)
            print(f"[+] 转换成功: {output_mrs}")

        except Exception as e:
            print(f"[-] 处理 {name} 失败: {e}")
            has_error = True
        finally:
            if os.path.exists(temp_src):
                os.remove(temp_src)

    if has_error:
        print("[!] 构建过程中存在失败项，终止工作流")
        sys.exit(1)

if __name__ == "__main__":
    main()