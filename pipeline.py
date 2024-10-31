from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import boto3

yourbucket = 'test'

schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("CustomerId", StringType(), True),
        StructField("FirstName", StringType(), True),
        StructField("LastName", StringType(), True)
    ])

# Thiết lập URL JDBC cho MySQL container
jdbc_url = "jdbc:mysql://mysql:3306/your_database"  # 'mysql' là tên dịch vụ của MySQL trong Docker Compose
table_name = "customer"

# Thiết lập URL JDBC cho MySQL container
properties = {
        "user": "root",
        "password": "root",
        "driver": "com.mysql.cj.jdbc.Driver"
    }

# Cấu hình thông tin MinIO
minio_endpoint = "http://minio:9000"  # Địa chỉ của MinIO
access_key = "minioadmin"
secret_key = "minioadmin"

def main():
    # Khởi tạo SparkSession với cấu hình kết nối tới MinIO
    spark = SparkSession.builder \
        .appName("ETL Pipeline") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.maximum", "100") \
        .getOrCreate()

     # Đọc file CSV với schema có sẵn
    df = spark.read.csv(
        "/data/customers.csv",         # Đường dẫn tới file CSV
        schema=schema,               # Sử dụng schema đã định nghĩa
        header=True,                 # Nếu file CSV có dòng tiêu đề
        sep=",",                     # Dấu phân cách trong CSV
        inferSchema=False            # Không cần Spark tự suy luận schema
    ) 

    # Ghi DataFrame trống vào MySQL, tạo bảng nếu chưa có
    df.write.jdbc(url=jdbc_url, table=table_name, mode="overwrite", properties=properties)

    # Đọc dữ liệu từ MySQL
    df = spark.read \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", table_name) \
        .option("user", "root") \
        .option("password", "root") \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .load()

    print(df.show(5))


    # Khởi tạo kết nối tới MinIO sử dụng Boto3
    s3_client = boto3.client(
        "s3",
        endpoint_url=minio_endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Tạo bucket trên MinIO
    bucket_name = "bucketauto"
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        print(f"Error creating bucket: {e}")


    # Bước 2: Lưu dữ liệu vào MinIO
    df.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(f"s3a://{bucket_name}/test.parquet")

    # Bước 3: Đọc dữ liệu từ MinIO
    minio_df = spark.read \
        .format("parquet") \
        .load(f"s3a://{bucket_name}/test.parquet")
    
    print(minio_df.show(5))

    # Bước 4: Lưu dữ liệu vào PostgreSQL
    # Ghi DataFrame xuống PostgreSQL
    minio_df.write.format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/target_database") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "customer") \
        .option("user", "target_user") \
        .option("password", "target_password") \
        .mode("append") \
        .save()
    
    # # Đọc dữ liệu từ PostgreSQL
    # df = spark.read.format("jdbc") \
    #     .option("url", "jdbc:postgresql://0.0.0.0:5432/target_database") \
    #     .option("driver", "org.postgresql.Driver") \
    #     .option("dbtable", "customer") \
    #     .option("user", "target_user") \
    #     .option("password", "target_password") \
    #     .load()

    # Dừng Spark session
    spark.stop()

if __name__ == "__main__":
    main()
