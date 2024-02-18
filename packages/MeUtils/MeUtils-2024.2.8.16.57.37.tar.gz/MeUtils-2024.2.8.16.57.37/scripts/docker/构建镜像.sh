#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/12/22 14:49
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :

docker build -t api-reverse .


# docker run -p 39999:8000 -e GITHUB_COPILOT_TOKEN=123 chatllm/api-reverse
# docker push chatllm/api-reverse