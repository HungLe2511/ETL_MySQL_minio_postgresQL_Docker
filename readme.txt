dau tien, ta prj2. Chay cau lenh : docker-compose up --build

Neu xuat hien loi : 
    spark-job-1  | py4j.protocol.Py4JJavaError: An error occurred while calling o46.load.
    spark-job-1  | : com.mysql.cj.jdbc.exceptions.CommunicationsException: Communications link failure

ta thuc hien thay doi ten host trong file pipeline.py dong thu 19 thanh : project2-mysql-1 or mysql

sau do ta se build lai docker-compose. Se gap loi :
    spark-job-1  | py4j.protocol.Py4JJavaError: An error occurred while calling o46.load.
    spark-job-1  | : java.sql.SQLSyntaxErrorException: Table 'your_database.customer' doesn't exist

    Day la do em chua tao 1 bang nao trong database cua SQL : gio ta se truy cap vao mysql tao bang :
    $ docker exec -it project2-mysql-1 mysql -u root -p
    root

    Sau do vao db, tao bang :
        mysql> use your_database
        mysql> create table customer (Id int, CustomerId VARCHAR(200),FirstName VARCHAR(200),LastName VARCHAR(200));

    Insert data tu file.csv vao:
    Day file csv vao trong mysql:
        docker cp customers.csv project2-mysql-1:/var/lib/mysql-files/file.csv

    Sau do insert data vao bang:
        LOAD DATA INFILE '/var/lib/mysql-files/file.csv'
        INTO TABLE customer
        FIELDS TERMINATED BY ','  
        LINES TERMINATED BY '\n'
        IGNORE 1 ROWS;  -- Nếu dòng đầu tiên là tiêu đề

    Sau do,rebuild lai docker :
        docker-compose up --build

    Ra log ntn la ok!
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

    Tiep den ta sap gap loi~, Do minio chua tao bucket:
        spark-job-1  | : org.apache.hadoop.fs.s3a.UnknownStoreException: `s3a://test/test.parquet': getFileStatus on s3a://test/test.parquet: com.amazonaws.services.s3.model.AmazonS3Exception: The specified bucket does not exist (Service: Amazon S3; Status Code: 404; Error Code: NoSuchBucket; Request ID: 1803131AB30E82C1; S3 Extended Request ID: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8; Proxy: null), S3 Extended Request ID: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8:NoSuchBucket: The specified bucket does not exist (Service: Amazon S3; Status Code: 404; Error Code: NoSuchBucket; Request ID: 1803131AB30E82C1; S3 Extended Request ID: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8; Proxy: null)
    Ta truy cap manual vao web UI bucket va tao 1 bucket ten : test
    Sau do Rebuild lai code : docker-compose up --build
    Done!!