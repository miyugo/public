# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 14:22:44 2018

@author: yunpeng.zhang
"""

from bottle import route, request, run
import os

#定义上传路径
path = 'c:/users/yunpeng.zhang/desktop/python/files'

def get_save_path_for_category(category):
    '''要在这里添加判断，判断文件夹是否存在，存在就直接返回新路径，不存在就新建一个'''
    newpath=path + '/' + category
    if os.path.exists(newpath):
        return newpath
    else:
        os.mkdir(newpath)
        return newpath

@route('/upload')
def upload():
    return '''
<html>
    <body> <form action='/upload' method='post' enctype='multipart/form-data'>
            Category:<input name='category' type='text'/>
            Select a file:<input name='upload' type='file'/>
            <input value='Start upload' type='submit'/>
            </form>
    </body>
</html> '''
@route('/upload',method='post')
def do_upload():
    Category=request.forms.get('category')
    upload=request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    if os.path.exists(get_save_path_for_category(Category)+'/'+upload.filename):
        return 'file is exist.'
    elif ext not in ('.png','.jpg','.jpeg'):
        return 'File extension not allowed.'
    else:
        save_path = get_save_path_for_category(Category)
        upload.save(save_path) # appends upload.filename automatically
        return 'OK'
run(host='localhost',port=8080,debug=True)