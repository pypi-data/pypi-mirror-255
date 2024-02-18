#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : auth
# @Time         : 2023/12/19 17:12
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

get_bearer_token = HTTPBearer()
