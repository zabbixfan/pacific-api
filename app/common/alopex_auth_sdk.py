#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request, g,redirect,make_response,jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as JwtSerializer
import functools,hashlib
from ApiResponse import ApiResponse,ResposeStatus
from config import Config

APP_ID = Config.APP_ID
APP_SECRET = Config.APP_SECRET
AUTH_SERVER_HOST = Config.AUTH_SERVER_HOST
AUTH_SERVER_LOGIN_URL = Config.AUTH_SERVER_LOGIN_URL
AUTH_SERVER_LOGOUT_URL = Config.AUTH_SERVER_LOGOUT_URL
def SignatureGeneration(res_dict={}, secret_key=""):
    """
    生成签名
    :param secret_key: 签名 Key
    :param time_out: 签名过期时间
    :param res_dict: 签名参数体
    :return:
    """
    key_list = res_dict.keys()
    key_list.sort()
    sign_str = u''
    for key in key_list:
        if not isinstance(res_dict.get(key), (dict, list)):
            sign_str += unicode(res_dict.get(key))
    # secret_key + value 组合字符串 md5 取中间16位
    sign_str = secret_key + sign_str
    sign = hashlib.md5(sign_str).hexdigest()[8:-8]
    return sign

class AccessTokenModel(object):
    def __init__(self, client_id, user):
        self.client_id = client_id
        self.user = user

    @classmethod
    def token2cls(cls, token,client_secret=APP_SECRET):
        if token:
            s = JwtSerializer(client_secret)
            try:
                data = s.loads(token)
                if "client_id" in data and "user" in data:
                    return cls(data["client_id"], data["user"])
                else:
                    return None
            except Exception,e:
                print e
                return None
        else:
            return None


def get_access_token():
    access_token = request.headers.get("Authorization")
    access_token = request.args.get("accesstoken") if access_token is None else access_token
    access_token = request.cookies.get("accesstoken") if access_token is None else access_token
    access_token = request.form.get("accesstoken") if access_token is None else access_token
    return access_token


def authorize(access_token):
    token_obj = AccessTokenModel.token2cls(access_token)

    if token_obj:
        return token_obj
    else:
        return None


def need_login(save_token_at_cookie=True):
    """
    身份验证装饰器
    :param save_token_at_cookie:
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def auth(*args, **kw):
            access_token = get_access_token()
            signature = request.headers.get("X-Signature")
            if access_token:
                user_obj = authorize(access_token)
                if user_obj:
                    # 已登录
                    g.user = user_obj.user
                    g.userID = user_obj.user.get('id')
                    #response = make_response(jsonify(func(*args, **kw)))
                    response = func(*args, **kw)
                    # if save_token_at_cookie:
                    #     if (not request.cookies.get("accesstoken")) or (access_token!=request.cookies.get("accesstoken")) :
                    #         response.set_cookie("accesstoken", access_token)
                    if g.user['loginName'] not in ['songcheng3215','fengjinchao2709']:
                        return ApiResponse('No permission', ResposeStatus.AuthenticationFailed)
                    return response
            elif signature:
                req = {}
                if request.form:
                    req = dict(req, **request.form.to_dict())
                if request.args:
                    req = dict(req, **request.args.to_dict())
                if request.json:
                    req = dict(req, **request.json)
                if signature == SignatureGeneration(req):
                    response = func(*args, **kw)
                    return response
                else:
                    return ApiResponse(None, ResposeStatus.SignFail)
            # else:
            #     # 未登录或登录失效
            #     return redirect("{0}?appid={1}&callback={2}".format(AUTH_SERVER_LOGIN_URL,APP_ID,request.url))
            else:
                return ApiResponse('Error user', ResposeStatus.AuthenticationFailed)

        return auth

    return decorator

def logout():
    """
    用户退出引入方法
    :return:
    """
    response = make_response(redirect("{0}?appid={1}&callback={2}".format(AUTH_SERVER_LOGOUT_URL, APP_ID, request.host)))
    response.delete_cookie('accesstoken')
    return response

def need_login2(roles=[],save_token_at_cookie=True):
    """
    身份验证装饰器
    :param save_token_at_cookie:
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def auth(*args, **kw):
            access_token = get_access_token()
            signature = request.headers.get("X-Signature")
            if access_token:
                user_obj = authorize(access_token)
                if user_obj:
                    # 已登录
                    g.user = user_obj.user
                    g.userID = user_obj.user.get('id')
                    #response = make_response(jsonify(func(*args, **kw)))
                    # if save_token_at_cookie:
                    #     if (not request.cookies.get("accesstoken")) or (access_token!=request.cookies.get("accesstoken")) :
                    #         response.set_cookie("accesstoken", access_token)
                    if roles and roles.__len__()>0:
                        if g.user.get("role") in roles:
                            return func(*args, **kw)
                    else:
                        return func(*args, **kw)

                    return ApiResponse('No permission', ResposeStatus.Powerless)
            elif signature:
                req = {}
                if request.form:
                    req = dict(req, **request.form.to_dict())
                if request.args:
                    req = dict(req, **request.args.to_dict())
                if request.json:
                    req = dict(req, **request.json)
                if signature == SignatureGeneration(req):
                    response = func(*args, **kwargs)
                    return response
                else:
                    return ApiResponse(None, ResposeStatus.SignFail)
            # else:
            #     # 未登录或登录失效
            #     return redirect("{0}?appid={1}&callback={2}".format(AUTH_SERVER_LOGIN_URL,APP_ID,request.url))
            else:
                return ApiResponse('Error user', ResposeStatus.AuthenticationFailed)

        return auth

    return decorator
