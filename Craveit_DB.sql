create database Craveit;

use Craveit;

create table Users(user_id int auto_increment primary key, user_name varchar(100) not null, email varchar(100) unique not null, password varchar(100) unique not null, DOB date not null, state varchar(100) not null, country varchar(100) not null, gender varchar(10) not null);
desc Users;
+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| user_id   | int          | NO   | PRI | NULL    | auto_increment |
| user_name | varchar(100) | NO   |     | NULL    |                |
| email     | varchar(100) | NO   | UNI | NULL    |                |
| password  | varchar(100) | NO   | UNI | NULL    |                |
| DOB       | date         | NO   |     | NULL    |                |
| state     | varchar(100) | NO   |     | NULL    |                |
| country   | varchar(100) | NO   |     | NULL    |                |
| gender    | varchar(10)  | YES  |     | NULL    |                |
+-----------+--------------+------+-----+---------+----------------+

create table recipes (recipe_id int auto_increment primary key, user_id int not null, recipe_name varchar(255) not null, description text not null, i
nstructions text not null, calories int, foreign key (user_id) references Users(user_id));
Query OK, 0 rows affected
desc recipes;
+--------------+--------------+------+-----+---------+----------------+
| Field        | Type         | Null | Key | Default | Extra          |
+--------------+--------------+------+-----+---------+----------------+
| recipe_id    | int          | NO   | PRI | NULL    | auto_increment |
| user_id      | int          | NO   | MUL | NULL    |                |
| recipe_name  | varchar(255) | NO   |     | NULL    |                |
| description  | text         | NO   |     | NULL    |                |
| instructions | text         | NO   |     | NULL    |                |
| calories     | int          | YES  |     | NULL    |                |
+--------------+--------------+------+-----+---------+----------------+
6 rows in set (0.00 sec)

create table ingredients (ing_id int auto_increment primary key, ing_name varchar(100) not null, img_url varchar(255));
Query OK, 0 rows affected (0.02 sec)

 desc ingredients;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| ing_id   | int          | NO   | PRI | NULL    | auto_increment |
| ing_name | varchar(100) | NO   |     | NULL    |                |
| img_url  | varchar(255) | YES  |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
3 rows in set (0.00 sec)

create table recipe_ingredients(recipe_id int not null, ing_id int not null, quantity varchar(50) not null, foreign key (recipe_id) references recipes(recipe_id), foreign key (ing_id) references ingredients(ing_id));
Query OK, 0 rows affected (0.06 sec)

desc recipe_ingredients;
+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| recipe_id | int         | NO   | MUL | NULL    |       |
| ing_id    | int         | NO   | MUL | NULL    |       |
| quantity  | varchar(50) | NO   |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
3 rows in set (0.00 sec)
