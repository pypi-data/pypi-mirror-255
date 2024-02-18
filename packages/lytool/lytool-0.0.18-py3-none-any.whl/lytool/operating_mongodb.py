from pymongo import MongoClient


class Operating_MongoDB():
    def __init__(self, database, host='127.0.0.1', port=27017):
        self.database = database
        self.host = host
        self.port = port

    def connect(self, collection):
        # 连接mongdb数据库，返回指定集合
        self.engine = MongoClient(host=self.host, port=self.port)
        return self.engine[self.database][collection]

    def mongodb_find_all(self, collection, condition=None):
        collection = self.connect(collection)  # 获取指定的集合
        if condition == None:  # 无条件查询全部
            all_info = collection.find()  # 返回集合中所有数据
        else:  # 有条件查询条件下的数据
            all_info = collection.find(condition)  # {'name':'cyl'}返回指定条件下的数据
        all_info_list = [i for i in all_info]
        self.engine.close()  # 关闭连接
        return all_info_list

    def mongodb_insert(self, collection, data):
        '''
        # 插入数据
        # collection:str 集合名字
        # data：list/dict 传入的数据
        '''
        collection = self.connect(collection)  # 获取指定集合
        if isinstance(data, dict):  # 判断数据是否为字典
            collection.insert(data)  # 插入一条数据
            # collection.insert_one(data)  # 插入一条数据
            print('插入1条数据')
        elif isinstance(data, list):  # 判断数据是否为列表
            collection.insert_many(data)  # 插入多条数据
            print('插入{}条数据'.format(len(data)))
        self.engine.close()

    def mongodb_save(self, collection, data):
        '''
        # 插入一条相同_id的数据，会更新这条数据
        # collection:str 集合名字
        # data：list/dict 传入的数据
        '''

        collection = self.connect(collection)  # 获取指定集合
        if isinstance(data, dict):  # 判断数据是否为字典
            collection.save(data)  # 插入一条数据
            # collection.insert_one(data)  # 插入一条数据
            print('插入1条数据')
        elif isinstance(data, list):  # 判断数据是否为列表
            collection.insert_many(data)  # 插入多条数据
            print('插入{}条数据'.format(len(data)))
        self.engine.close()

    def mongodb_update_one(self, collection, condition, updateData):
        # 更新匹配到的第一条数据
        collection = self.connect(collection)
        collection.update_one(condition, updateData)
        self.engine.close()

    def mongodb_update_many(self, collection, condition, updateData):
        # 更新匹配到的所有数据
        collection = self.connect(collection)
        collection.update_many(condition, updateData)
        self.engine.close()

    def mongodb_delete_one(self, collection, condition):
        # 删除匹配到的第一条数据
        collection = self.connect(collection)
        collection.delete_one(condition)
        self.engine.close()

    def mongodb_delete_many(self, collection, condition):
        # 删除匹配到的所有数据
        collection = self.connect(collection)
        collection.delete_many(condition)
        self.engine.close()

    def mongodb_duplication(self):
        self.mong


if __name__ == '__main__':
    operating_MongoDB = Operating_MongoDB('gl')
    # 查询student集合中的所有数据
    print(operating_MongoDB.mongodb_find_all('userInfo'))

    # 查询student集合中名字为小高的数据
    # print(operating_MongoDB.mongodb_find_all('student', {'name':'小高'}))

    # 插入数据
    # operating_MongoDB.mongodb_insert('student',
    #                                  [
    #                                      {'name': 'cyl', 'age': 18, 'gender': 1, 'address': 'chendu', 'isDelete': 0},
    #                                      {'name': 'psx', 'age': 28, 'gender': 0, 'address': 'chendu', 'isDelete': 0}
    #                                  ])

    # 更新匹配到的第一条数据
    # operating_MongoDB.mongodb_update_one('student', {'name':'cyl'}, {'$set':{'age': 32}})
    # print(operating_MongoDB.mongodb_find_all('student', {'name':'cyl'}))

    # 更新匹配到的所有数据
    # operating_MongoDB.mongodb_update_many('student', {'name': 'psx'}, {'$set': {'age': 32}})
    # print(operating_MongoDB.mongodb_find_all('student', {'name': 'psx'}))

    # 删除匹配到的第一条数据
    # operating_MongoDB.mongodb_delete_one('student', {'name':'cyl'})
    # print(operating_MongoDB.mongodb_find_all('student'))

    # 删除匹配到的所有数据
    # operating_MongoDB.mongodb_delete_many('student', {'name': '小高'})
    # print(operating_MongoDB.mongodb_find_all('student'))
