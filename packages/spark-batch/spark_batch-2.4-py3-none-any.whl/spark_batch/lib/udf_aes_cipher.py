from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark.sql.types import StringType
from pyspark.sql.functions import udf
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import binascii

class AESCipher:
    def __init__(self, key_str, iv_str):
        self.key = key_str.encode() #('utf-8')
        self.iv = iv_str.encode() #('utf-8')

    # 디버깅을 위한 코드 추가
    def encrypt(self, value):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted_value = cipher.encrypt(pad(value.encode(), AES.block_size))
        encoded_value = base64.b64encode(encrypted_value).decode()

        return encoded_value

    def decrypt(self, encrypted_value):
        try:
            encrypted_value = base64.b64decode(encrypted_value)
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted_value = unpad(cipher.decrypt(encrypted_value), AES.block_size)
            decoded_value = decrypted_value.decode()
            return decoded_value
        except binascii.Error as e:
            # 오류가 발생한 경우, null 값을 반환하거나 다른 값을 처리할 수 있습니다.
            return None

    def regist(self, spark):    
        # UDF 등록
        encrypt_udf = udf(self.encrypt, StringType())
        decrypt_udf = udf(self.decrypt, StringType())

        spark.udf.register("encode", encrypt_udf)
        spark.udf.register("decode", decrypt_udf)

        return (encrypt_udf,  decrypt_udf)

## Spark 세션 생성
#spark = SparkSession.builder.appName("AESCipherExample").getOrCreate()
#spark.sparkContext.addPyFile(f"lib/pycryptodome-py{py}.tgz")
#
## 예제 데이터 생성
#data = [("John",), ("Alice",), ("Bob",)]
#columns = ["name"]
## DataFrame 생성
#df = spark.createDataFrame(data, columns)
