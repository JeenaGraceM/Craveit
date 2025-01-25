create database Craveit;

use Craveit;

create table Users(user_id int auto_increment primary key, user_name varchar(100) not null, email varchar(100) unique not null, password varchar(100) unique not null, DOB date not null, state varchar(100) not null, country varchar(100) not null, gender varchar(10) not null);
desc Users

/*
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

*/

create table recipes (recipe_id int auto_increment primary key, user_id int not null, recipe_name varchar(255) not null, description text not null, i
nstructions text not null, calories int, foreign key (user_id) references Users(user_id));

desc recipes;
 /*
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
*/

create table ingredients (ing_id int auto_increment primary key, ing_name varchar(100) not null, img_url varchar(255));

 desc ingredients;

 /*
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| ing_id   | int          | NO   | PRI | NULL    | auto_increment |
| ing_name | varchar(100) | NO   |     | NULL    |                |
| img_url  | varchar(255) | YES  |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
3 rows in set (0.00 sec)
*/

create table recipe_ingredients(recipe_id int not null, ing_id int not null, quantity varchar(50) not null, foreign key (recipe_id) references recipes(recipe_id), foreign key (ing_id) references ingredients(ing_id));

desc recipe_ingredients;
/*
+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| recipe_id | int         | NO   | MUL | NULL    |       |
| ing_id    | int         | NO   | MUL | NULL    |       |
| quantity  | varchar(50) | NO   |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
3 rows in set (0.00 sec)
*/

create table dietary_category(diet_id int auto_increment primary key, diet_name varchar(100) not null);

desc dietary_category;
/*
+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| diet_id   | int          | NO   | PRI | NULL    | auto_increment |
| diet_name | varchar(100) | NO   |     | NULL    |                |
+-----------+--------------+------+-----+---------+----------------+
2 rows in set (0.00 sec)
*/

 create table health_issues(issue_id int auto_increment primary key, issue varchar(100) not null);

desc health_issues;

/*
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| issue_id | int          | NO   | PRI | NULL    | auto_increment |
| issue    | varchar(100) | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
2 rows in set (0.00 sec)
*/

create table user_issue(user_id int not null, issue_id int not null, foreign key (user_id) references Users(user_id), foreign key (issue_id) refe
rences health_issues(issue_id));

 desc user_issue;

 /*
+----------+------+------+-----+---------+-------+
| Field    | Type | Null | Key | Default | Extra |
+----------+------+------+-----+---------+-------+
| user_id  | int  | NO   | MUL | NULL    |       |
| issue_id | int  | NO   | MUL | NULL    |       |
+----------+------+------+-----+---------+-------+
2 rows in set (0.00 sec)
*/

 create table recipe_search_history(id int primary key, user_id int not null, search_term varchar(255));

 desc recipe_search_history;

 /*
+-------------+--------------+------+-----+---------+-------+
| Field       | Type         | Null | Key | Default | Extra |
+-------------+--------------+------+-----+---------+-------+
| id          | int          | NO   | PRI | NULL    |       |
| user_id     | int          | NO   |     | NULL    |       |
| search_term | varchar(255) | YES  |     | NULL    |       |
+-------------+--------------+------+-----+---------+-------+
3 rows in set (0.00 sec)
*/

create table alternative_ingredients(id int primary key, recipe_id int not null, missing_ingredient varchar(100) not null, suggested_ingredient varchar(100) not null, foreign key(recipe_id) references recipes(recipe_id));


 desc alternative_ingredients;
 /*
+----------------------+--------------+------+-----+---------+-------+
| Field                | Type         | Null | Key | Default | Extra |
+----------------------+--------------+------+-----+---------+-------+
| id                   | int          | NO   | PRI | NULL    |       |
| recipe_id            | int          | NO   | MUL | NULL    |       |
| missing_ingredient   | varchar(100) | NO   |     | NULL    |       |
| suggested_ingredient | varchar(100) | NO   |     | NULL    |       |
+----------------------+--------------+------+-----+---------+-------+
4 rows in set (0.00 sec)
*/

create table recipe_issues(recipe_id int not null,issue_id int not null,  foreign key(issue_id) references health_issues(issue_id), foreign key(recipe_id) references recipes(recipe_id));

desc recipe_issues;
/*
 desc recipe_issues;
+-----------+------+------+-----+---------+-------+
| Field     | Type | Null | Key | Default | Extra |
+-----------+------+------+-----+---------+-------+
| recipe_id | int  | NO   | MUL | NULL    |       |
| issue_id  | int  | NO   | MUL | NULL    |       |
+-----------+------+------+-----+---------+-------+
2 rows in set (0.00 sec)
*/