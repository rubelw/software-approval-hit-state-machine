#!/bin/bash
set -e -x
echo "Starting setup..." > /var/log/user_data.log
sudo yum update -y >> /var/log/user_data.log 2>&1
sudo yum -y install mariadb105-server.x86_64 >> /var/log/user_data.log 2>&1
echo "Start mariadb service" > /var/log/user_data.log
sudo service mariadb start >> /var/log/user_data.log 2>&1

echo "Creating database db" >> /var/log/user_data.log 2>&1
sudo mysql -h ${rds_address} -uadmin -p${rds_password} completeMysql -e "create database db;" >> /var/log/user_data.log 2>&1
sudo mysql -h ${rds_address} -uadmin -p${rds_password} db -e "CREATE TABLE requested_tokens (token VARCHAR(50) PRIMARY KEY);" >> /var/log/user_data.log 2>&1
sudo mysql -h ${rds_address} -uadmin -p${rds_password} db -e "CREATE TABLE requested_approval (id INT AUTO_INCREMENT PRIMARY KEY, token VARCHAR(50) NOT NULL, cve VARCHAR(50) NOT NULL,vendor VARCHAR(50) NOT NULL,software VARCHAR(100),requestor VARCHAR(100),approver VARCHAR(100),requested_at DATETIME(6) NOT NULL,FOREIGN KEY (token) REFERENCES requested_tokens(token) ON DELETE CASCADE);" >> /var/log/user_data.log 2>&1
sudo mysql -h ${rds_address} -uadmin -p${rds_password} db -e "CREATE TABLE approved_software (id INT AUTO_INCREMENT PRIMARY KEY, cve VARCHAR(50) NOT NULL,vendor VARCHAR(50) NOT NULL,software VARCHAR(100),requestor VARCHAR(100),approver VARCHAR(100),approved_at DATETIME(6) NOT NULL);" >> /var/log/user_data.log 2>&1
sudo mysql -h ${rds_address} -uadmin -p${rds_password} db -e "INSERT INTO requested_tokens (token) VALUES('valid-token');" >> /var/log/user_data.log 2>&1
