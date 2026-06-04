# coding=utf-8
# -----道阻且长 行则将至-------
# ---  版权所有 侵权必究  ----
# ---- 一切解释权归本人所有 ----
# 日 期：2024/9/1 
# 时 间：17:08
import csv

from config.config import MySQL_Config,log
import MySQLdb
def find_all_table_name():
    """
    获取数据库中全部的表名
    :return:
    List
    """
    connection = None
    try:
        # 创建数据库连接
        connection = MySQLdb.connect(**MySQL_Config)

        # 创建游标对象
        cursor = connection.cursor()

        # 执行查询以获取所有表名
        cursor.execute("SHOW TABLES;")

        # 获取所有表名
        tables = cursor.fetchall()

        # 提取表名并返回
        table_names = [table[0] for table in tables]
        res=[]
        for t in table_names:
            for suffix in ['_train', '_test']:
                if str(t).endswith(suffix):
                    tab=str(t).removesuffix(suffix)
                    if tab not in res:
                        res.append(tab)

        return res

    except MySQLdb.Error as e:
        print("Error while connecting to MySQL:", e)
        return []

    finally:
        # 关闭游标和连接
        try:
            if cursor:
                cursor.close()
            if connection and connection.open:
                connection.close()
        except Exception as e:
            log.error(f"请检查数据库配置")
            raise Exception(f"数据库配错误")
"""
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, random_state=42)
"""


def get_table_columns(table_name,cols=[]):
    """
    根据表名获取MySQL数据库表的属性列信息。



    返回:
    - 一个列表，包含元组，每个元组代表一列的信息（如列名、数据类型等）
    """
    try:
        # 连接到MySQL数据库
        conn = MySQLdb.connect(**MySQL_Config)
        cursor = conn.cursor()

        # 执行SQL查询以获取表的列信息
        query = f"DESCRIBE {table_name};"
        cursor.execute(query)

        # 获取并返回查询结果
        columns = cursor.fetchall()
        columns = [(column[0], column[1]) for column in columns]  # 通常我们只关心列名、数据类型和是否允许NULL
        cursor.close()
        conn.close()
        if len(cols) == 0:
            return columns
        else:
            result = []
            for c in columns:
                if c[0] in cols:
                    result.append(c)
            return result

    except MySQLdb.Error as e:
        log.error(f"Error while connecting to MySQL: {e}")
        return []

def fetch_data_from_table(table_name,cols=[],limit=-1):
    """
    从数据库中获取指定表的数据。
    """
    try:
        # 连接到数据库
        db = MySQLdb.connect(**MySQL_Config)

        # 创建一个游标对象
        cursor = db.cursor()

        # 构建 SQL 查询
        if len(cols) == 0:
            sql_query = f"SELECT * FROM {table_name}"
        else:
            sql_query = f"SELECT {','.join(cols)} FROM {table_name}"

        if limit > 0:
            sql_query += f" LIMIT {limit}"
        # 执行 SQL 查询
        cursor.execute(sql_query)

        # 获取所有结果
        results = cursor.fetchall()



        # 关闭游标和数据库连接
        cursor.close()
        db.close()
        # for row in results:
        #     for column in row:

        return results

    except MySQLdb.Error as e:
        log.error(e)
        return None

def mysql_table_to_csv(table_name, csv_file_path, cols=[], limit=-1):
    try:
        # 获取列名
        columns_info = get_table_columns(table_name, cols)
        column_names = [col[0] for col in columns_info]

        # 获取表数据
        data = fetch_data_from_table(table_name, column_names, limit)

        if data is None:
            return

        # 写入 CSV 文件
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            # 写入列名
            csv_writer.writerow(column_names)
            # 写入数据行
            for row in data:
                csv_writer.writerow(row)

        print(f"数据已成功从表 {table_name} 导出到 {csv_file_path}")

    except Exception as e:
        print(f"发生错误: {e}")



if __name__ == '__main__':
    print(get_table_columns('bitcoin_price_train'))

