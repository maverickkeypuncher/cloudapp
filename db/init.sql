CREATE DATABASE cloudapp;

USE cloudapp;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO users (username, password)
VALUES ('admin', 'admin123');

CREATE TABLE provisioning_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    datacenter VARCHAR(50) NOT NULL,
    cpu VARCHAR(50) NOT NULL,
    ram VARCHAR(50) NOT NULL,
    num_servers INT NOT NULL,
    storage VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
