from pyspark.sql import SparkSession

yourbucket = 'test'

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

    # Thiết lập URL JDBC cho MySQL container
    jdbc_url = "jdbc:mysql://project2-mysql-1:3306/your_database"  # 'mysql' là tên dịch vụ của MySQL trong Docker Compose
    table_name = "customer"

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
    # Bước 2: Lưu dữ liệu vào MinIO
    df.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(f"s3a://{yourbucket}/test.parquet")

    # Bước 3: Đọc dữ liệu từ MinIO
    minio_df = spark.read \
        .format("parquet") \
        .load(f"s3a://{yourbucket}/test.parquet")
    
    print(minio_df.show(5))

    # Bước 4: Lưu dữ liệu vào PostgreSQL
    # Ghi DataFrame xuống PostgreSQL
    minio_df.write.format("jdbc") \
        .option("url", "jdbc:postgresql://project2-postgres-1:5432/target_database") \
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
