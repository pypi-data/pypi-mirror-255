from sqlalchemy import create_engine
import pandas as pd
import json
from sqlalchemy.exc import ResourceClosedError


class Operating_MySql():
    def __init__(self, database, drive='pymysql', userName='root', password='135cylpsx', host='127.0.0.1', port='3306'):
        self.drive, self.userName, self.password, self.host, self.port, self.database = drive, userName, password, host, port, database

    def connect(self):
        '''数据库连接器'''
        engine = create_engine(
            'mysql+{}://{}:{}@{}:{}/{}?charset=utf8'.format(self.drive, self.userName, self.password, self.host,
                                                            self.port, self.database))
        return engine

    def dfImportDatabase(self, df, table, if_exists='append'):
        '''
            df导入到mysql
            if_exists ——
                append：如果表存在，则将数据添加到这个表的后面；
                fail：如果表存在就不操作；
                replace：如果存在表，删了，重建
        '''
        engine = self.connect()
        pd.io.sql.to_sql(df, name=table, con=engine, schema=self.database, if_exists=if_exists, index=False)
        engine.dispose()

    def readDfImportDatabase(self, path, table, sheet=0, is_exists='replace'):
        '''
            功能：读取excel转df再导入database
            if_exists ——
                append：如果表存在，则将数据添加到这个表的后面；
                fail：如果表存在就不操作；
                replace：如果存在表，删了，重建
        '''
        df = pd.read_excel(path, sheet_name=sheet)
        self.dfImportDatabase(df, table, is_exists)

    def getDf(self, sql):
        '''从数据库中获取DataFrame'''
        engine = self.connect()
        df = pd.read_sql_query(sql, engine)
        engine.dispose()
        return df

    def getJson(self, sql):
        '''获取多行列表数据，并转为json'''
        df = self.getDf(sql)
        return json.dumps(
            {"code": 200, "msg": {'total': len(df), 'rows': list(json.loads(df.to_json(orient='index')).values())}})

    def getDictList(self, sql):
        '''
        获取多行数据，并转为字典列表
        :param sql: ’select * from tableName‘
        :return: [{'a':'1','b':'2'},{'a':'3','b':'4'}]
        '''
        df = self.getDf(sql)
        return list(json.loads(df.to_json(orient='index')).values())

    def getList(self, fieldName, tableName):
        '''
        获取多行数据，并转为列表
        :param fieldName: 要查询的字段名
        :param tableName: 要在哪个表里查
        :return: ['1','2']  # [value1, value2]
        '''
        df = self.getDf(f'select {fieldName} from {tableName}')
        return [i[fieldName] for i in list(json.loads(df.to_json(orient='index')).values())]

    def getListWhere(self, fieldName, tableName, where):
        '''
        获取多行数据，并转为列表
        :param fieldName: 要查询的字段名
        :param tableName: 要在哪个表里查
        :return: ['1','2']  # [value1, value2]
        '''
        df = self.getDf(f'''select {fieldName} from {tableName} where {where}''')
        return [i[fieldName] for i in list(json.loads(df.to_json(orient='index')).values())]

    def getTextWhere(self, fieldName, tableName, where):
        '''
        获取多行数据，并转为列表
        :param fieldName: 要查询的字段名
        :param tableName: 要在哪个表里查
        :return: '1'
        '''
        df = self.getDf(f'''select {fieldName} from {tableName} where {where}''')
        try:
            return [i[fieldName] for i in list(json.loads(df.to_json(orient='index')).values())][0]
        except IndexError:
            return None

    def getSum(self, fieldName, tableName, where):
        '''
        获取多行数据，并转为列表
        :param fieldName: str,要查询的字段名
        :param tableName: str,要在哪个表里查
        :param where: str,条件
        :return: float or in  # 1.0+1.0
        '''
        return sum(self.getListWhere(fieldName, tableName, where))

    def getLen(self, fieldName, tableName, where):
        '''
        获取多行数据，并转为列表，返回列表长度
        :param fieldName: str,要查询的字段名
        :param tableName: str,要在哪个表里查
        :param where: str,条件
        :return: int
        '''
        return len(self.getListWhere(fieldName, tableName, where))

    def getId(self, tableName):
        '''
        获取某表的id字段
        :param tableName:
        :return: [1,2]
        '''
        return self.getList('id', tableName)

    def getIdWhere(self, tableName, where):
        '''
        获取某表的id字段
        :param tableName:
        :return: [1,2]
        '''
        return self.getListWhere('id', tableName, where)

    def get_Id(self, tableName, where):
        '''
        example： o_m.get_Id('content', f'id={contentId}')
        :param tableName: 要查询的表
        :param where: 条件
        :return: _id的值
        '''
        return self.getListWhere('_id', tableName, where)[0]

    def getClassification(self, sql1, sql2, sql3):
        # 获取分类数据
        df1 = self.getDf(sql1)
        df2 = self.getDf(sql2)
        df3 = self.getDf(sql3)
        data_dict = {
            'first_list': list(json.loads(df1.to_json(orient='index')).values()),
            'second_list': list(json.loads(df2.to_json(orient='index')).values()),
            'third_list': list(json.loads(df3.to_json(orient='index')).values()),
        }
        return json.dumps({"code": 200, "msg": {"rows": data_dict}})

    def getCategoryProductInfomation(self, *args):
        '''
        将一级分类、二级分类、三级分类、商品信息拼接成json嵌套
        :param args: sql
        :return:{"id":"1", "name":"一级分类名称", "secend":[{"id":"1", "name":"二级分类名称1", "third":[...]},{...}]}
        '''
        first = self.getDictList(args[0])  # 一级分类信息
        secend = self.getDictList(args[1])  # 二级分类信息
        third = self.getDictList(args[2])  # 三级分类信息
        goods_info_list = json.loads(args[3])['msg']['rows']  # 商品信息

        # 三级添加商品
        for index_3, category_3 in enumerate(third):
            third[index_3]['product'] = []
            for goods in goods_info_list:
                if category_3['id'] == goods['third_classification_id']:
                    goods_dict = goods.copy()  # 深拷贝
                    goods_dict.pop('third_classification_id', None)  # 删除多余字段
                    third[index_3]['product'].append(goods_dict)
        # 二级添加三级
        for index_2, category_2 in enumerate(secend):
            secend[index_2]['third'] = []
            for item in third:
                if category_2['id'] == item['prev_id']:
                    item_dict = item.copy()  # 深拷贝
                    item_dict.pop('prev_id', None)  # 删除多余字段
                    secend[index_2]['third'].append(item_dict)
        # 一级添加二级
        for index_1, category_1 in enumerate(first):
            first[index_1]['secend'] = []
            for item in secend:
                if category_1['id'] == item['prev_id']:
                    item_dict = item.copy()  # 深拷贝
                    item_dict.pop('prev_id', None)  # 删除多余字段
                    first[index_1]['secend'].append(item_dict)
        return first

    def getRowList(self, sql):
        '''
        获取一行中的为字符串列表的字段:"['a','b']"
        :param sql: 'select fieldName from tableName where id="id"'
        :return: ['a','b']
        '''
        data = self.getDictList(sql)
        return eval(list(data[0].values())[0])

    def getRowString(self, sql):
        '''
        获取一行中的为字符串字段:"a"
        :param sql: 'select fieldName from tableName where id="id"'
        :return: 'a'
        '''
        data = self.getDictList(sql)
        return list(data[0].values())[0]

    def isExistAtColumns(self, value, fieldName, tableName):
        '''
        查询某值是否在于列表中（某个字段的某张表中）
        :param value: 要查询的值
        :param fieldName: 字段名（mysql中）
        :param tableName: 表名（mysql中）
        :return: 存在返回True，不存在返回False
        '''
        dataList = self.getList(fieldName, tableName)
        if value in dataList:
            return True
        else:
            return False

    def isEqual(self, value, fieldName, tableName, where):
        '''
        判断某值是否等于数据库中的某值
        :param value: 要判断的值
        :param fieldName: 字段名（mysql中）
        :param tableName: 表名（mysql中）
        :param where: 查询条件
        :return: 相等True，不相等False
        '''
        data = self.getListWhere(fieldName, tableName, where)
        if value in data:
            return True
        else:
            return False

    def insert(self, sql):
        '''
        插入数据
        原生sql语法：
        INSERT INTO 表名称 VALUES (值1, 值2,....)
        INSERT INTO table_name (列1, 列2,...) VALUES (值1, 值2,....)
        '''
        engine = self.connect()
        try:
            pd.read_sql_query(sql, engine)
        except ResourceClosedError as e:
            pass
        engine.dispose()

    def update(self, sql):
        '''
        更新数据
        原生sql语法：
        update userinfo set follow="{followList}" where openid="{followerOpenid}
        '''
        engine = self.connect()
        try:
            pd.read_sql_query(sql, engine)
        except ResourceClosedError as e:
            pass
        engine.dispose()

    def delete(self, sql):
        '''删除数据'''
        engine = self.connect()
        try:
            pd.read_sql_query(sql, engine)
        except ResourceClosedError as e:
            pass
        engine.dispose()



if __name__ == '__main__':
    operating_mysql = Operating_MySql(database='college')

    # .df_import_database 读取df存入数据库
    # df = pd.DataFrame({
    #     'a': ['1'],
    #     'b': ['2']
    # })
    # operating_mysql.df_import_database(df, 'testtable')

    # .insert 数据插入数据库 自增的id，插入时填0，即可id自增
    # operating_mysql.insert(sql='''insert into learninfo values
    #     (0, 1, 1, 0.0, 0, 0.0, 0.0),
    #     (0, 2, 1, 0.0, 0, 0.0, 0.0);
    # ''')

    # .update 更新数据
    operating_mySql.update(sql='''
        update learninfo set  learnTime=0.5, learnStatus=1, currentTime=0.4, duration=60.1 where userId=2 and contentId=5
    ''')
