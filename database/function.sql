create function change_student_password(student_no CHAR(7), student_password VARCHAR(512),
                                        student_new_password VARCHAR(512))
    RETURNS INT DETERMINISTIC
BEGIN
    DECLARE user_old_password VARCHAR(512);
    DECLARE user_new_password VARCHAR(512);
    DECLARE AFFECTED_ROWS int DEFAULT 0;
    DECLARE ERROR_MESSAGE varchar(128);
    SET user_old_password := MD5(student_password);
    SET user_new_password := MD5(student_new_password);

    if student_new_password REGEXP '^[0-9]+$' or student_new_password REGEXP '^[A-Za-z]+$' then
        set ERROR_MESSAGE = "Password should be alphanumeric";
        signal sqlstate '45000' set message_text = ERROR_MESSAGE;
    end if;

    if LENGTH(student_new_password) < 8 THEN
        set ERROR_MESSAGE = "Password is too short";
        signal sqlstate '45000' set message_text = ERROR_MESSAGE;
    END IF;
    if LENGTH(student_new_password) > 20 THEN
        set ERROR_MESSAGE = "Password is too long";
        signal sqlstate '45000' set message_text = ERROR_MESSAGE;
    END IF;

    UPDATE student
    SET student.password = user_new_password
    WHERE student.student_no = student_no
      AND student.password = user_old_password;
    SELECT ROW_COUNT() into AFFECTED_ROWS;
    RETURN AFFECTED_ROWS;
END;



create function change_professor_password(professor_no CHAR(5), professor_password VARCHAR(512),
                                          professor_new_password VARCHAR(512))
    RETURNS INT DETERMINISTIC
BEGIN
    DECLARE user_old_password VARCHAR(512);
    DECLARE user_new_password VARCHAR(512);
    DECLARE AFFECTED_ROWS int DEFAULT 0;
    DECLARE ERROR_MESSAGE varchar(128);

    SET user_old_password := MD5(professor_password);
    SET user_new_password := MD5(professor_new_password);

    if professor_new_password REGEXP '^[0-9]+$' or professor_new_password REGEXP '^[A-Za-z]+$' then
        set ERROR_MESSAGE = "Password should be alphanumeric";
        signal sqlstate '45000' set message_text = ERROR_MESSAGE;
    end if;
    if LENGTH(professor_new_password) < 8 THEN
        set ERROR_MESSAGE = "Password is too short";
        signal sqlstate '45000' set message_text = ERROR_MESSAGE;
    END IF;
    if LENGTH(professor_new_password) > 20 THEN
        set ERROR_MESSAGE = "Password is too long";
        signal sqlstate '45000' set message_text = ERROR_MESSAGE;
    END IF;
    UPDATE professor
    SET professor.password = user_new_password
    WHERE professor.professor_no = professor_no
      AND professor.password = user_old_password;
    SELECT ROW_COUNT() into AFFECTED_ROWS;
    RETURN AFFECTED_ROWS;
END;

CREATE FUNCTION role_define(user varchar(10))
    RETURNS varchar(10) DETERMINISTIC
Begin
    DECLARE role varchar(10);
    if Length(user) = 5
    Then
        set role = 'Professor';
    End if;
    if Length(user) = 7
    Then
        set role = 'Student';
    End if;
    Return role;
End;

CREATE FUNCTION login_user(username VARCHAR(7), user_password VARCHAR(512))
    RETURNS int DETERMINISTIC
BEGIN
    DECLARE user_hashed_password VARCHAR(512);
    DECLARE LOGIN_STATUS int DEFAULT 0;
    SET user_hashed_password := MD5(user_password);
    SELECT count(*)
    INTO LOGIN_STATUS
    FROM student
    WHERE student.student_no = username
      AND student.password = user_hashed_password;
    IF LOGIN_STATUS = 0 THEN
        SELECT count(*)
        INTO LOGIN_STATUS
        FROM professor
        WHERE professor.professor_no = username
          AND professor.password = user_hashed_password;
    END IF;
    RETURN LOGIN_STATUS;
END;

create function logout(user varchar(10))
    returns int deterministic
BEGIN
    UPDATE last_login set log_in = 0 where last_login.username = user;
    return 1;
end;

create function create_exam(course char(8), name_in varchar(20), start timestamp, end timestamp, exam_time integer)
    returns int deterministic
BEGIN
    declare examm_id int;
    insert into exam(name, start_time, end_time, exam_duration, course_id)
    values (name_in, start, end, exam_time, course);
    select exam_id into examm_id from exam where course = exam.course_id and exam.name = name_in;
    return examm_id;
end;

create function create_question_exam(description varchar(512), fc varchar(128), sc varchar(128), tc varchar(128),
                                     ftc varchar(128), id_exam varchar(10), answer varchar(2), score int)
    returns int deterministic
BEGIN
    insert into exam_question(question_description, first_choice, second_choice, third_choice, fourth_choice, exam_id,
                              correct_answer, question_score)
    values (description, fc, sc, tc, ftc, id_exam, answer, score);
    return 1;
end;

create function create_homework(hw_name varchar(30), course char(8), till TIMESTAMP)
    returns int deterministic
BEGIN
    DECLARE idd int;
    insert into homework(name, course_id, deadline) values (hw_name, course, till);
    select homework_id into idd from homework where hw_name = homework.name and homework.course_id = course;
    return idd;
end;

create function create_homework_question(id int, description varchar(20), answer varchar(20), score int)
    returns int deterministic
BEGIN
    insert into homework_question(homework_id, hw_description, correct_answer, hw_question_score)
    values (id, description, answer, score);
    return 1;
end;


create function get_hw_deadline(hw_id int)
    returns TIMESTAMP deterministic
BEGIN
    DECLARE deadlinee TIMESTAMP;
    select deadline into deadlinee from homework where homework_id = hw_id;
    return deadlinee;
end;

create function time_update(time_input TIME, id int, s_n char(7), course char(8))
    returns int deterministic
BEGIN
    DECLARE ex int default 0;
    select count(*)
    into ex
    from student_hw_participation
    where student_hw_participation.hw_id = id
      and student_hw_participation.student_no = s_n;
    IF ex = 1 then
        UPDATE student_hw_participation
        set time_enter= time_input
        where student_hw_participation.student_no = s_n
          and student_hw_participation.hw_id = id;
    end if;
    if ex = 0 then
        INSERT INTO student_hw_participation values (s_n, id, time_input, course, 0);
    end if;
    return 1;
end;

create function upload(student_no char(7), hw_id int, hwq_id int, answer varchar(128), time_inserted TIMESTAMP,
                       course char(8))
    RETURNS int deterministic
BEGIN
    DECLARE deadlinee TIMESTAMP;
    declare temp int;
    select deadline into deadlinee from homework where homework_id = hw_id;
    if time_inserted > deadlinee then
        return 0;
    end if;
    select count(*)
    into temp
    from student_hw_question_participation
    where student_hw_question_participation.student_no = student_no
      and student_hw_question_participation.hw_id = hw_id
      and student_hw_question_participation.hw_question_id = hwq_id
      and student_hw_question_participation.course_id = course;

    if temp = 0 then
        INSERT INTO student_hw_question_participation
        values (student_no, hw_id, hwq_id, answer, time_inserted, course, -1);
    end if;
    if temp != 0 then
        UPDATE student_hw_question_participation
        set student_hw_question_participation.answer= answer
        where student_hw_question_participation.student_no = student_no
          and student_hw_question_participation.hw_id = hw_id
          and student_hw_question_participation.hw_question_id = hwq_id
          and student_hw_question_participation.course_id = course;
    end if;
    return 1;
end;


create function submit_answer(q_id int, s_no char(7), answer char(1), ex_id int, course char(8))
    returns int deterministic
begin
    declare canswer char(1);
    select correct_answer into canswer from exam_question where exam_question.question_id = q_id;
    if canswer = answer then
        insert into exam_answer values (q_id, s_no, answer, 1, ex_id, course);
    end if;
    if canswer != answer then
        insert into exam_answer values (q_id, s_no, answer, 0, ex_id, course);
    end if;
    return 1;
end;

create function first_time(s_no char(7), ex_id int)
    returns int deterministic
begin
    DECLARE temp int DEFAULT 0;
    select count(*) into temp from student_exam_attended where student_no = s_no and exam_id = ex_id;
    if temp = 0 then
        INSERT INTO student_exam_attended values (s_no, ex_id,-1);
        return 1;
    end if;
    return 0;
end;
create function cal_exam_grade(s_no char(7), ex_id int)
    returns int deterministic
begin
    DECLARE grade int default 0;
    DECLARE len int default 0;
    select count(question_id) into len from exam_answer where student_no = s_no and exam_id = ex_id;
    if len != 0 then
    select sum(score) / count(question_id) into grade from exam_answer where student_no = s_no and exam_id = ex_id;
    end if;
    UPDATE student_exam_attended set final_grade = grade where student_no =s_no and exam_id = ex_id;
    return grade;
end;
create function submit_grade(hwid int,studento char(7), hwq_id int, course char(8),gradee int)
returns int deterministic
begin

    UPDATE student_hw_question_participation set grade = gradee where hw_id = hw_id and student_no = studento and hw_question_id = hwq_id and course_id = course;
    return 1;
end;
