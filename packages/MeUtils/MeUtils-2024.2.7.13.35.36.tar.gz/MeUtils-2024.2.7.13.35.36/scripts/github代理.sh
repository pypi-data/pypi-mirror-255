#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2024/1/17 14:08
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
git config --unset http.proxy
git config --unset https.proxy

#使用socks5代理（推荐）
git config --global htgit config --global --unset http.proxy
git config --global --unset https.proxy
tp.https://github.com.proxy socks5://127.0.0.1:1081
#使用http代理（不推荐）
git config --global http.https://github.com.proxy http://127.0.0.1:8001
