create table student
(
    national_code char(10) unique,
    student_no    char(7) primary key,
    name_fa       varchar(30) NOT NULL,
    name_en       varchar(30) NOT NULL,
    father_name   varchar(30) NOT NULL,
    birth_date    DATE        NOT NULL,
    mobile        varchar(20) NOT NULL,
    major         varchar(30) NOT NULL,
    password      varchar(512),
    email         varchar(64)
);
create table professor
(
    national_code char(10) unique,
    professor_no  char(5) primary key,
    name_fa       varchar(30)                            NOT NULL,
    name_en       varchar(30)                            NOT NULL,
    father_name   varchar(30)                            NOT NULL,
    birth_date    DATE                                   NOT NULL,
    mobile        varchar(20),
    department    varchar(60)                            NOT NULL,
    title         ENUM ('استاد', 'استادیار', 'دانش‌یار') NOT NULL,
    password      varchar(512),
    email         varchar(64)
);
create table course
(
    course_id    char(8) primary key,
    course_name  varchar(60) NOT NULL,
    professor_no char(5)     NOT NULL,
    foreign key (professor_no) references professor (professor_no)
);
create table classroom
(
    course_id  char(8),
    student_no char(7),
    primary key (course_id, student_no),
    foreign key (course_id) references course (course_id),
    foreign key (student_no) references student (student_no)
);
create table exam
(
    exam_id       int auto_increment primary key,
    name          varchar(50),
    start_time    timestamp NOT NULL,
    end_time      timestamp NOT NULL,
    exam_duration int       NOT NULL,
    course_id     char(8)   not null,
    foreign key (course_id) references course (course_id)
);
create table exam_question
(
    question_id          int primary key auto_increment,
    question_description varchar(512) not null,
    first_choice         varchar(128) not null,
    second_choice        varchar(128) not null,
    third_choice         varchar(128) not null,
    fourth_choice        varchar(128) not null,
    exam_id              int,
    correct_answer       ENUM ('A','B','C','D'),
    question_score       int          not null,
    FOREIGN KEY (exam_id) references exam (exam_id)

);
create table last_login
(
    ID       int primary key AUTO_INCREMENT,
    username varchar(7),
    time     TIME,
    log_in   bool
);
create table homework
(
    homework_id int auto_increment,
    name        varchar(30) not null,
    course_id   char(8),
    deadline    TIMESTAMP,
    primary key (homework_id),
    foreign key (course_id) references course (course_id)
);
create table homework_question
(
    hw_question_id    int auto_increment,
    homework_id       int,
    hw_description    varchar(20),
    correct_answer    varchar(20),
    hw_question_score int DEFAULT 0,
    foreign key (homework_id) references homework (homework_id),
    primary key (hw_question_id)
);
create table student_exam_attended
(
    student_no char(7),
    exam_id    int,
    final_grade int DEFAULT 0,
    primary key (student_no, exam_id)
);
create table exam_answer
(
    question_id INT,
    student_no  CHAR(7),
    user_answer ENUM ('A', 'B', 'C', 'D') NOT NULL,
    score       INT DEFAULT 0,
    exam_id     int,
    course_id   char(8),
    PRIMARY KEY (question_id, student_no, exam_id),
    FOREIGN KEY (student_no) REFERENCES student (student_no),
    FOREIGN KEY (question_id) REFERENCES exam_question (question_id),
    foreign key (exam_id) references exam (exam_id),
    foreign key (course_id) references course (course_id)
);
create table student_hw_participation
(
    student_no  char(7),
    hw_id       int       not null,
    time_enter  TIMESTAMP not null,
    course_id   char(8),
    total_grade int default -1,
    primary key (student_no, hw_id, time_enter),
    foreign key (hw_id) references homework (homework_id),
    foreign key (student_no) references student (student_no),
    foreign key (course_id) references course (course_id)
);
create table student_hw_question_participation
(
    student_no     char(7),
    hw_id          int not null,
    hw_question_id int not null,
    answer         varchar(128),
    time_inserted  timestamp,
    course_id      char(8),
    grade          int default -1,
    primary key (student_no, hw_id, hw_question_id, answer),
    foreign key (hw_id) references homework (homework_id),
    foreign key (student_no) references student (student_no),
    foreign key (hw_question_id) references homework_question (hw_question_id),
    foreign key (course_id) references course (course_id)
);
