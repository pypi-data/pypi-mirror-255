import re
from pyspark.sql.types import StructType, StructField, DecimalType, StringType, IntegerType, DateType, TimestampType, BooleanType, FloatType, LongType


def parseSourceObject(source_object):
    # source_object 값이 이미 리스트인 경우 그대로 반환
    if isinstance(source_object, list):
        return source_object
    # source_object 값을 공백 또는 쉼표로 분할하여 어레이로 변환
    parts = [x.strip() for x in source_object.replace('\n', ' ').split()]
    return parts

def parseSourceObjectTest() :
    # 테스트
    source_object = "aaa bbb"
    result = parseSourceObject(source_object)
    print(result)  # ["aaa", "bbb"]

def toTempView(filename):
    # 앞자리 숫자 제거
    filename = re.sub(r'^\d+', '', filename)

    # 앞자리 마침표 제거
    filename = re.sub(r'^\.', '', filename)

    # 확장자명 제거
    parts = filename.rsplit('.', 1)
    if len(parts) > 1:
        filename = parts[0]

    # "_*" 또는 "*"에 해당하는 이하 제거
    filename = re.sub(r'(_|\*)[^_]*$', '', filename)

    return filename

def toTempViewTest() :
    # 예시 파일 이름
    file_names = [
        "16.card_hdong_mth_int_by_int.csv",
        ".card_hdong_mth_int_by_int.txt",
        "TB_HH_PPLTN_INFO_*.csv"
    ]

    for file_name in file_names:
        result = toTempView(file_name)
        print(result)    

def toCustomSchema(column_data_types):
    custom_fields = []
    supported_data_types = {
        "decimal": DecimalType,
        "string": StringType(),
        "integer": IntegerType(),
        "long": LongType(),
        "float": FloatType(),
        "date": DateType(),
        "timestamp": TimestampType(),
        "boolean": BooleanType(),
        # 다른 데이터 타입을 필요에 따라 추가할 수 있습니다.
    }
    
    for column, data_type in column_data_types.items():
        if isinstance(data_type, tuple):
            data_type_str = data_type[0]
            nullable = data_type[1]
        else:
            data_type_str = data_type
            nullable = True

        # 정규식을 사용하여 decimal(x) 또는 decimal(x, y) 형식을 해석
        decimal_match = re.match(r"decimal\((\d+)(?:,(\d+))?\)", data_type_str)
        if decimal_match:
            x = int(decimal_match.group(1))
            y = int(decimal_match.group(2)) if decimal_match.group(2) else 0
            field = StructField(column, supported_data_types["decimal"](x, y), nullable)
            custom_fields.append(field)
        elif data_type_str in supported_data_types:
            field = StructField(column, supported_data_types[data_type_str], nullable)
            custom_fields.append(field)
        else:
            raise ValueError(f"Unsupported data type: {data_type_str} for column: {column}")
    
    customSchema = StructType(custom_fields)
    return customSchema


def toCustomSchemaTest() :

    # column_data_types 딕셔너리 예시
    column_data_types = {
        "SORT_NO": ("decimal(10)", True),
        "OTHER_COLUMN": ("decimal(8,2)", False),
        "ANOTHER_COLUMN": "decimal(6)",
        "DESCRIPTION": ("string", False),
        "QUANTITY": "integer",
        "ORDER_DATE": "date",
        "TIMESTAMP_COLUMN": "timestamp",
        "IS_NO": "boolean",
    }

    schema = toCustomSchema(column_data_types)
    print(schema) 


def toTargetCondition(df, key):
    if df is None:
        return None

    keylist = [row[key] for row in df.select(key).distinct().collect()]

    sql_condition = "WHERE {} IN ({})".format(key, ", ".join(["'{}'".format(value) for value in keylist]))
    return sql_condition


import time


class Timer:
    def __init__(self):
        self.start_time = time.time()
        self.last_tab_time = self.start_time

    def tab(self):
        """
        탭을 누를 때 이후 경과 시간을 출력하고, 누적된 시간을 갱신합니다.
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_tab_time
        self.last_tab_time = current_time
        return elapsed_time

    def elapsed(self):
        """
        전체 경과 시간을 반환하면서 누적된 시간을 출력합니다.
        """
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        return elapsed_time
