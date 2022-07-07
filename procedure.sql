create procedure prof_all_exam_of_course(course char(8))
BEGIN
    select exam_id, name from exam where course_id = course;
end;
create procedure prof_all_homeworks_of_course(course char(8))
BEGIN
    select homework_id, name from homework where course_id = course;
end;

create procedure student_all_exam_of_course(course char(8))
BEGIN
    select exam_id, name from exam where course_id = course;
end;

create procedure student_all_homeworks_of_course(course char(8))
BEGIN
    select homework_id, name from homework where course_id = course;
end;

create procedure show_homework(course char(8), hw_id int)
begin
    select hw_description, hw_question_id
    from homework
             natural join homework_question
    where course_id = course
      and homework_id = hw_id;
end;
create procedure show_history_of_upload(st_no char(7))
BEGIN
    select * from student_hw_question_participation where student_no = st_no;
end;

create procedure get_all_homeworks_asnwers_prof(course char(8), hw_id int)
begin
    select student_no, hw_question_id, answer, time_inserted, grade
    from student_hw_question_participation
    where course_id = course
      and hw_id = student_hw_question_participation.hw_id;
end;

create procedure enter_ok_exam(exam_id int)
begin
    select start_time, end_time, exam_duration from exam where exam.exam_id = exam_id;
end;

create procedure show_questions(exam_id int)
begin
    select question_id, question_description, first_choice, second_choice, third_choice, fourth_choice
    from exam_question
    where exam_question.exam_id = exam_id;
end;

create procedure review_exam(username char(7),ex_id int)
begin
    select question_description,user_answer,correct_answer,score from exam_answer natural join exam_question where student_no =username and exam_id = ex_id;
end;

create procedure get_hw_info(hw_id int)
begin
    select hw_question_id,correct_answer from homework_question where homework_id = hw_id;
end;

create procedure choose_student(hwid int,course char(8))
begin
    select student_no from student_hw_question_participation where hw_id = hwid and course_id = course;
end;

create procedure a_student_answers(stud_id char(7),hwid int)
begin
    select hw_question_id,answer from student_hw_question_participation where stud_id = stud_id and hw_id = hwid;
end;

create procedure get_all_exams_answers_prof(course char(8), examid int)
begin
    select student_no, question_id, user_answer,score
    from exam_answer
    where course_id = course
      and exam_id = examid ;
end;
