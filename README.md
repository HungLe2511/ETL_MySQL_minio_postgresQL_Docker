1. chạy lệnh build docker :
```sh
docker-compose up --build
```
    

2. Nếu xuất hiện lỗi :
```sh
spark-job-1  | py4j.protocol.Py4JJavaError: An error occurred while calling o46.load.
spark-job-1  | : com.mysql.cj.jdbc.exceptions.CommunicationsException: Communications link failure
```
    2.1 Ta thực hiện đổi tên host của container MySQL trong file pipeline.py Dòng thứ 19 thành : `project2-mysql-1` or `mysql`

4. Sau đó thực hiên build lại docker-compose :
```sh
docker-compose up --build
```
5. Sẽ gặp lỗi :
 ```sh
 spark-job-1  | py4j.protocol.Py4JJavaError: An error occurred while calling o46.load.
 spark-job-1  | : java.sql.SQLSyntaxErrorException: Table 'your_database.customer' doesn't exist
```
Đây là do chưa tạo bảng customer trong mySQL,giờ sẽ truy cập vào mySQL để tạo bảng :
 ```sh
 $ docker exec -it project2-mysql-1 mysql -u root -p
 root
```
6. Vào db mySQL dể tạo bảng:
 ```sh
mysql> use your_database
mysql> create table customer (Id int, CustomerId VARCHAR(200),FirstName VARCHAR(200),LastName VARCHAR(200));
```
7. Insert data từ file.csv:
7.1 Đẩy file.csv vào mySQL:
 ```sh
docker cp customers.csv project2-mysql-1:/var/lib/mysql-files/file.csv
```
7.2 Sau đó insert data vào bảng:
 ```sh
LOAD DATA INFILE '/var/lib/mysql-files/file.csv'
 INTO TABLE customer
 FIELDS TERMINATED BY ','  
 LINES TERMINATED BY '\n'
 IGNORE 1 ROWS;
```
8. Sau đó,chạy lại docker :
```sh
docker-compose up --build
```
Ra log ntn la ok!
```sh
Check log : 
spark-job-1  | +---+---------------+---------+---------+
spark-job-1  | | Id|     CustomerId|FirstName| LastName|
spark-job-1  | +---+---------------+---------+---------+
spark-job-1  | |  1|EB54EF1154C3A78|  Heather| Callahan|
spark-job-1  | |  2|10dAcafEBbA5FcA| Kristina|  Ferrell|
spark-job-1  | |  3|67DAB15Ebe4BE4a|   Briana| Andersen|
spark-job-1  | |  4|6d350C5E5eDB4EE|    Patty|    Ponce|
spark-job-1  | |  5|5820deAdCF23EFe| Kathleen|Mccormick|
spark-job-1  | +---+---------------+---------+---------+
```

9. Tiếp đến sẽ gặp lỗi, Do minio chưa tạo buget:
```sh
spark-job-1  | : org.apache.hadoop.fs.s3a.UnknownStoreException: `s3a://test/test.parquet': getFileStatus on s3a://test/test.parquet: com.amazonaws.services.s3.model.AmazonS3Exception: The specified bucket does not exist (Service: Amazon S3; Status Code: 404; Error Code: NoSuchBucket; Request ID: 1803131AB30E82C1; S3 Extended Request ID: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8; Proxy: null), S3 Extended Request ID: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8:NoSuchBucket: The specified bucket does not exist (Service: Amazon S3; Status Code: 404; Error Code: NoSuchBucket; Request ID: 1803131AB30E82C1; S3 Extended Request ID: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8; Proxy: null)
```
9.1 Truy cập vào web UI bucket và tạo 1 bucket tên : test
9.2 Chạy lại docker : 
 ```sh
docker-compose up --build
```
Done!!
