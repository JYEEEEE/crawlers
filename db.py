"""
连接数据库

doc: https://www.runoob.com/python3/python-mongodb.html
"""
import pymongo

# mongodb配置
host = '192.168.10.21'
port = 27017

mongoclient = pymongo.MongoClient("mongodb://{host}:{port}/".format(host=host, port=port))

if __name__ == '__main__':
    # 测试数据库连接是否正常，直接运行这个脚本就可以
    try:
        mongoclient.list_database_names()
    except Exception as e:
        print('test connect failed.')
    else:
        print('connect success')
