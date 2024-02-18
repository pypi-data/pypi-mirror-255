#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/12/18 12:06
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :

docker run -d --restart always --name PandoraNext --net=bridge \
  -p 39101:8181 \
  -v ./data:/data \
  -v ./sessions:/root/.cache/PandoraNext \
  pengzhile/pandora-next
