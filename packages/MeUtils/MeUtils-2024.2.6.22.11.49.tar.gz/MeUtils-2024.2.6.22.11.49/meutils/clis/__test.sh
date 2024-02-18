#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2024/1/3 09:51
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :
#python -m meutils.clis.browser prun --headless --url  https://chat.deepseek.com --storage-state "deepseek_*.json"

#python -m meutils.clis.browser refresh --no-headless --delay 1 --url  https://chat.deepseek.com --storage-state "deepseek_*.json"

#python -m meutils.clis.browser prun --headless --kwargs '{"task": "deepseek"}' --url  https://chat.deepseek.com --storage-state "./deepseek_*.json"

#python browser.py prun --kwargs '{"task": "deepseek", "user_file":"deepseek.txt"}' --no-headless


python browser.py refresh --delay 5 --storage-state "kimi_*.json" --no-headless --no-only-once