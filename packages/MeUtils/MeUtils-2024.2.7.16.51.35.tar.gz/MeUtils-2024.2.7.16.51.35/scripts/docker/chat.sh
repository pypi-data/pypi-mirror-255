#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/12/15 11:24
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  : https://github.com/lobehub/lobe-chat?tab=readme-ov-file
#
#docker rm -f Lobe-Chat
#docker pull lobehub/lobe-chat
#docker run -d --network=host -e OPENAI_API_KEY=sk-XXXX -e ACCESS_CODE="" --name=Lobe-Chat --restart=always lobehub/lobe-chat
#docker images | grep 'lobehub/lobe-chat' | grep -v 'latest' | awk '{print $3}' | xargs docker rmi

docker run -d -p 39777:3210 \
  -e OPENAI_API_KEY=sk-xxxx \
  -e OPENAI_PROXY_URL=https://api.chatllm.vip/v1 \
  -e ACCESS_CODE=chatllm \
  lobehub/lobe-chat

# https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web
docker run --name chatgpt-next-web \
  --restart=always \
  -d -p 39771:3000 \
  -e BASE_URL=http://api.chatllm.vip \
  -e CUSTOM_MODELS=+gemini-pro,+kimi,+kimi-32k,+kimi-128k,+kimi-256k,+deepseek,-gpt-3.5-turbo-0301,-gpt-3.5-turbo-0613,-gpt-3.5-turbo-16k-0613,-gpt-4-0314,-gpt-4-0613,-gpt-4-32k-0314,-gpt-4-32k-0613 \
  yidadaa/chatgpt-next-web

# https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web
docker run --name chatgpt-next-web \
  --restart=always \
  -d -p 39771:3000 \
  -e BASE_URL=http://api.chatllm.vip \
  -e OPENAI_API_KEY=sk-xxxx \
  -e CODE=chatfire,chatllm \
  -e CUSTOM_MODELS=+gpt-4-all,+gemini-pro,+qwen,+glm,+baichuan,+kimi,+ERNIE-Bot-turbo,+deepseek,-gpt-3.5-turbo-0301,-gpt-3.5-turbo-0613,-gpt-3.5-turbo-16k-0613,-gpt-4-0314,-gpt-4-0613,-gpt-4-32k-0314,-gpt-4-32k-0613 \
  yidadaa/chatgpt-next-web
