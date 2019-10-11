# -*- coding:utf-8 -*-  
#basic
from django.db import models

#http
from django.http import JsonResponse, HttpResponse

#time, jwt
import time,datetime, jwt

#models
from data.models import as_staff, as_project

#ldap...
import os, math, sys, ldap 

private_key = "9j7hBII9fRxPMYoYd4rc"

def get_staff_info_by_mail(request):
    jwt_encode = jwt.encode({
        'mail_name': 'di.lan@mihoyo.com', 
        'time': time.strftime("%Y-%m-%d %H:%M", time.localtime())
    }, private_key, algorithm='HS256')

    #return HttpResponse(jwt_encode)
    query_jwt = request.GET['query']
    data = {}
    try:
        query_json = jwt.decode(jwt_encode, private_key, algorithms=['HS256'])
        if query_json['time'] == time.strftime("%Y-%m-%d %H:%M", time.localtime()):
            mail_name = query_json['mail_name']
            staff_list = as_staff.objects.exclude(did_id=13).filter(mail_name=mail_name)
            msg = 'success'
            for i in staff_list.values():
                data['mail_name'] = i['mail_name']
                data['chinese_name'] = i['chinese_name']
                data['project_name'] = staff_list.get().pid.chinese_project_name
            retcode = 0
        else:
            retcode = -2
            msg = 'time_out'
    except:
        retcode = -1
        msg = 'system_error'
    json_content = {
        'retcode': retcode,
        'msg': msg,
        'data': data
    }
    return JsonResponse(json_content)

#查询时间合法性判断(参数1：查询字符串，参数2：查询失效时间)
def is_time_valid(query_json, time_out_limit):
    return query_json['time'] + time_out_limit * 60 * 100 > time.time()     

def get_jwt_token(request):
    #jwt相关配置
    private_key = "9j7hBII9fRxPMYoYd4rc"
    try:
        username = request.GET['username']
        password = request.GET['password']
    except:
        return HttpResponse()
    jwt_encode = jwt.encode(
    {
        'username': username, 
        'password': password, 
        'time': time.time()
    }
    , private_key, algorithm='HS256')

    Server = "ldap://192.168.10.16:389"  
    baseDN = "cn=users,dc=miHoYo,dc=com"  
    searchScope = ldap.SCOPE_SUBTREE 
    searchFilter = "ou=dept"
    retrieveAttributes = None
    conn = ldap.initialize(Server)  
    conn.set_option(ldap.OPT_REFERRALS, 0)  
    conn.protocol_version = ldap.VERSION3 

    retcode = conn.simple_bind_s(username, password)
    conn.unbind()
    return HttpResponse(jwt_encode)
    return HttpResponse(retcode)

def domain_user_auth(request):
    #Ldap相关配置
    Server = "ldap://192.168.10.16:389"  
    baseDN = "ou=dept,dc=miHoYo,dc=com"
    searchScope = ldap.SCOPE_SUBTREE 
    searchFilter = "ou=dept"
    retrieveAttributes = None
    conn = ldap.initialize(Server)  
    conn.set_option(ldap.OPT_REFERRALS, 0)  
    conn.protocol_version = ldap.VERSION3 

    #GET数据获取
    query_jwt = request.GET['query']
    data = {}

    try:
        query_json = jwt.decode(query_jwt, private_key, algorithms=['HS256'])
        #查询时间合法性判断(参数1：查询字符串，参数2：查询失效时间(分钟))
        time_mark = is_time_valid(query_json, 10)
        if time_mark == True:
            username = query_json['username'] + '@mihoyo.com'
            password = query_json['password']
            if password == '':
                msg = 'invalid_password'
                retcode = -102
            else:
                try:
                    conn.timeout = 10
                    if conn.simple_bind_s(username, password):
                        data['username'] = username
                        try:
                            retrieveAttributes = ['cn','sAMAccountName']
                            searchFilter = "sAMAccountName=" + query_json['username']
                            #data["ldap_req"] = searchFilter 
                            ldap_result_id = conn.search(baseDN,searchScope,searchFilter,retrieveAttributes) 
                            result_type, result_data = conn.result(ldap_result_id, 0)
                            #data["ldap_rsp"] = result_data
                            if len(result_data) > 0: 
                                ldap_data = result_data[0][0]
                                ldap_split = ldap_data.split(",")
                                data['member_of'] = []
                                for filter_ in ldap_split:
                                    if "CN=" in filter_:
                                        data['chinese_name'] = filter_.replace("CN=","")
                                        continue
                                    if "OU=" in filter_:
                                        data['member_of'].append(filter_.replace("OU=",""))
                                        continue
                        except Exception as e:
                            #data['error'] = str(e)
                            pass
                        data['time'] = int(time.time())
                        msg = 'success'
                    retcode = 0
                except:
                    msg = 'auth_failed'
                    retcode = -101
        else:
            msg = 'time_out'
            retcode = -2
    except (TypeError,ValueError) as e:
        print(e)
        msg = 'system_error'
        retcode = -1
    conn.unbind()
    json_content = {
        'retcode': retcode,
        'msg': msg,
        'data': data
    }
    return JsonResponse(json_content)
