CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TYPE degree_t as enum('bachelor', 'master', 'specialist');
CREATE TYPE study_form_t as enum('fulltime', 'extramural', 'evening');
CREATE TYPE education_form_t as enum('budget', 'contract');


CREATE TABLE users (
    user_id serial PRIMARY KEY,
    name VARCHAR (200) NOT NULL,
    -- auth
    hashed_password VARCHAR (200),
    email VARCHAR (100) UNIQUE,
    -- register info
    verification_code UUID DEFAULT uuid_generate_v4(),
    -- info
    telephone VARCHAR (20),
    city VARCHAR (50),
    info TEXT,
    vk_link VARCHAR (100),
    instagram_link VARCHAR (100),
    fb_link VARCHAR (100),
    linkedin_link VARCHAR (100)
);

CREATE table student_group (
    group_name VARCHAR (50) PRIMARY KEY,
    department VARCHAR (50) NOT NULL,
    course_no integer NOT NULL,
    CONSTRAINT valid_course_no CHECK (0 <= course_no and course_no <= 10)
);

CREATE table student(
    user_id integer REFERENCES users (user_id) UNIQUE NOT NULL,
    PRIMARY KEY (user_id),
    group_name VARCHAR (50) REFERENCES student_group (group_name) NOT NULL,
    entry_year     integer,
    CONSTRAINT valid_entry_year CHECK (1900 <= entry_year and entry_year <= 2100),
    degree         degree_t,
    study_form     study_form_t,
    education_form education_form_t
);

CREATE TABLE professors(
     user_id integer REFERENCES users (user_id) UNIQUE NOT NULL,
     PRIMARY KEY (user_id)
);

CREATE TABLE course(
    course_id serial PRIMARY KEY,
    name VARCHAR (50) NOT NULL,
    description TEXT
);

CREATE TABLE course_material (
    course_id integer REFERENCES course (course_id) NOT NULL,
    name VARCHAR (50) NOT NULL,
    PRIMARY KEY (name),
    description TEXT,
    add_time DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE course_to_professor (
    course_id integer REFERENCES course (course_id) NOT NULL,
    professor_id integer REFERENCES professors (user_id) NOT NULL,
    PRIMARY KEY (course_id, professor_id)
);

CREATE TABLE course_to_editor (
    course_id integer REFERENCES course (course_id) NOT NULL,
    student_id integer REFERENCES student (user_id),
    PRIMARY KEY (course_id, student_id)
);

CREATE TABLE group_to_course (
    group_name VARCHAR (50) REFERENCES student_group (group_name) NOT NULL,
    course_id integer REFERENCES course (course_id) NOT NULL,
    PRIMARY KEY (group_name, course_id)
);

CREATE TABLE assignee_task (
    course_id integer REFERENCES course (course_id) NOT NULL,
    name VARCHAR (50) NOT NULL,
    PRIMARY KEY (name),
    start_time timestamp NOT NULL,
    end_time timestamp NOT NULL,
    description TEXT
);


CREATE TABLE assignee_submit (
    assignee_name varchar (50) REFERENCES assignee_task (name) NOT NULL,
    student_id integer REFERENCES users (user_id) NOT NULL,
    PRIMARY KEY (assignee_name, student_id),
    submit_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    solution TEXT
);

create or replace function f_assignee_submit_time_valid(assignee_name varchar(50), submit_time timestamp) returns bool as
$func$
select EXISTS (
        select 1 from assignee_task
        where assignee_name = assignee_task.name
        and assignee_task.start_time <= submit_time
        and submit_time <= assignee_task.end_time);
$func$ language sql stable;

ALTER TABLE assignee_submit ADD CONSTRAINT check_submit_time
CHECK (f_assignee_submit_time_valid(assignee_name, submit_time));


create or replace function f_assignee_submit_user_valid(assignee_name varchar(50), student_id integer) returns bool as
$func$
select EXISTS (
    select 1
    from assignee_task
    JOIN course ON assignee_task.course_id = course.course_id
    JOIN group_to_course gtc on course.course_id = gtc.course_id
    JOIN student_group sg on gtc.group_name = sg.group_name
    JOIN student on sg.group_name = student.group_name
    WHERE student.user_id = student_id AND assignee_task.name = assignee_name);
$func$ language sql stable;


ALTER TABLE assignee_submit ADD CONSTRAINT check_assignee_user_id
CHECK (f_assignee_submit_user_valid(assignee_name, student_id));