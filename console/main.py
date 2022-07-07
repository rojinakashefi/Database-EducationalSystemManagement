from datetime import datetime
import mysql.connector
from mysql.connector import Error
import json


def load_tables():
  f = open('data.json')
  data = json.load(f)
  import_student(data)
  import_professor(data)
  import_course(data)
  import_classroom(data)


def import_student(data):
  insertIntoStudents = "INSERT INTO student(national_code, student_no, name_fa, name_en, father_name, birth_date, mobile, major) VALUES "
  for i in data["students"]:
    insertIntoStudents += f"('{i['national_code']}', '{i['student_no']}', '{i['name_fa']}', '{i['name_en']}', '{i['father_name']}', '{i['birth_date']}', '{i['mobile']}', '{i['major']}') ,"
  insertIntoStudents = insertIntoStudents[:len(insertIntoStudents) - 1]
  cursor.execute(insertIntoStudents)
  connection.commit()


def import_professor(data):
  insertIntoProfessor = "INSERT INTO professor(national_code, professor_no, name_fa, name_en, father_name, birth_date, mobile, department, title) VALUES "
  for i in data["faculty"]:
    insertIntoProfessor += f"('{i['national_code']}', '{i['professor_no']}', '{i['name_fa']}', '{i['name_en']}', '{i['father_name']}', '{i['birth_date']}', '{i['mobile']}', '{i['department']}','{i['title']}'),"
  insertIntoProfessor = insertIntoProfessor[:len(insertIntoProfessor) - 1]
  cursor.execute(insertIntoProfessor)
  connection.commit()


def import_course(data):
  insertIntoCourse = "INSERT INTO course(course_id, course_name, professor_no) VALUES "
  for i in data["courses"]:
    insertIntoCourse += f"('{i['id']}', '{i['name']}', '{i['professor_no']}'),"
  insertIntoCourse = insertIntoCourse[:len(insertIntoCourse) - 1]
  cursor.execute(insertIntoCourse)
  connection.commit()


def import_classroom(data):
  insertIntoClassroom = "INSERT INTO classroom(course_id, student_no) VALUES "
  for i in data["classrooms"]:
    insertIntoClassroom += f"('{i['course_id']}', '{i['student_no']}'),"
  insertIntoCourse = insertIntoClassroom[:len(insertIntoClassroom) - 1]
  cursor.execute(insertIntoCourse)
  connection.commit()


def program_starts():
  while True:
    username, password, status = login()
    if status == 1:
      cursor.execute(f"SELECT role_define('{username}');")
      role = cursor.fetchall()[0][0]
      show_menu(role, username, password)
    else:
      print('Please try again')


def login():
  print("Please Enter your username:")
  username = input()
  print("Please Enter your password:")
  password = input()
  temp = f"SELECT login_user('{username}', '{password}');"
  cursor.execute(temp)
  result = cursor.fetchall()
  login_status = 0
  if result[0][0] == 1:
    print('login successful')
    login_status = 1
    current_time = datetime.now().strftime("%H:%M:%S")
    current_user = f"INSERT INTO last_login(username, time, log_in) VALUES ('{username}' , '{current_time}','1');"
    cursor.execute(current_user)
    connection.commit()
  else:
    print("login FAILD. wrong password")
  return username, password, login_status


def show_menu(role, username, password):
  print('choose an action:')
  print(f"{1}) Change password: ")
  print(f'{2}) Show courses')
  print(f'{3}) Logout')
  if role == 'Student':
    print(f'{4}) List of exams and homeworks')
    print(f'{5}) Enter an exam')
    print(f'{6}) Upload homeworks')
    print(f'{7}) Show homework uploads')
  if role == 'Professor':
    print(f'{4}) List of student of class')
    print(f'{5}) List of exams and homeworks of class')
    print(f'{6}) Create exam')
    print(f'{7}) Create homework')
    print(f'{8}) see answers for exams and homework')
    print(f'{9}) Grade homework')
  action = input()
  if action == '1':
    change_password(role, username, password)
  if action == '2':
    show_courses(role, username)
  if action == '3':
    logout(username)
    program_starts()
  if action == '4' and role == 'Professor':
    show_student_of_prof(username)
  if action == '4' and role == 'Student':
    exams_hw_student(username)
  if action == '5' and role == 'Professor':
    exams_hw_prof(username)
  if action == '5' and role == 'Student':
    enter_exam_mode(username)
  if action == '6' and role == 'Professor':
    create_exam(username)
  if action == '6' and role == 'Student':
    upload_homework(username)
  if action == '7' and role == 'Student':
    show_homework_upload(username)
  if action == '7' and role == 'Professor':
    create_homework(username)
  if action == '8':
    choose_exam_hw(username)
  if action == '9':
    grade_hw(username)
  show_menu(role, username, password)


def grade_hw(username):
  print('choose the course you want to grade its homework:')
  results = show_courses('Professor', username)
  selected_course = int(input())
  selected_course = results[selected_course - 1][0]
  cursor.callproc('student_all_homeworks_of_course', [selected_course])
  for result in cursor.stored_results():
    hws = result.fetchall()
  print(f'HOMEWORKS of course {selected_course} : ')
  if len(hws) != 0:
    for hw in hws:
      print(hw[1], end=' | ')
    print()
    print('please choose the homework you want to check: ')
    choose_hw = int(input())
    hw_id = hws[choose_hw - 1][0]
    cursor.execute(f"SELECT get_hw_deadline('{hw_id}');")
    temp = cursor.fetchall()
    if temp[0][0] > datetime.now():
      print('First let the deadline finish then you can check')
    else:
      print('Grade homworks:')
      cursor.callproc('get_hw_info', [hw_id])
      for result in cursor.stored_results():
        q_of_hws = result.fetchall()
      if len(q_of_hws) != 0:
        cursor.callproc('choose_student', [hw_id, selected_course])
        for result in cursor.stored_results():
          s_hws = result.fetchall()
        if len(s_hws) != 0:
          for s in s_hws:
            print(s[0], end=' | ')
          print()
          print('please choose the student you want to check: ')
          choose_s = int(input())
          s_id = s_hws[choose_s - 1][0]
          cursor.callproc('a_student_answers', [s_id, hw_id])
          for result in cursor.stored_results():
            student_answer = result.fetchall()

          if len(student_answer) != 0:
            for answer in student_answer:
              for q_id in q_of_hws:
                if answer[0] == q_id[0]:
                  print(f'questionid: {answer[0]}')
                  print('enter score')
                  score = int(input())
                  cursor.execute(F'select submit_grade({hw_id},{s_id},{q_id[0]},{selected_course},{score})')
                  if cursor.fetchall()[0][0] == 1:
                    connection.commit()
                    print('Score submitted')
                  continue
      else:
        print('no student submitted this homework')



  else:
    print('no hws sets for this course')


def enter_exam_mode(username):
  print('choose the course you want to see exams and homeworks for:')
  results = show_courses('Student', username)
  selected_course = int(input())
  selected_course = results[selected_course - 1][0]
  cursor.callproc('student_all_exam_of_course', [selected_course])
  for result in cursor.stored_results():
    exams = result.fetchall()
  print(f'EXAMS of course {selected_course}: ')
  if len(exams) != 0:
    for exam in exams:
      print(exam[1], end=' | ')
    print('please choose an exam you want to see the result: ')
    choose_exam = int(input())
    if choose_exam != -1:
      exam_id = exams[choose_exam - 1][0]
      cursor.callproc('enter_ok_exam', [exam_id])
      for result in cursor.stored_results():
        ex_times = result.fetchall()
      if len(ex_times) != 0:
        for time in ex_times:
          if time[1] < datetime.now():
            calculate_exam(username, exam_id)
            print('Exam time over')
            break
          elif time[0] <= datetime.now() <= time[1]:
            time_startt = datetime.now()
            print(f'Exam started in {time_startt} ')
            exam_participate(selected_course, time_startt, time[1], time[2], username, exam_id)
    print()
  else:
    print('no exam sets for this course')


def exam_participate(course, start, end, duration, username, exam_id):
  cursor.execute(f"select first_time('{username}','{exam_id}');")
  one_time = cursor.fetchall()[0][0]
  if one_time == 1:
    connection.commit()
    while (datetime.now() - start).total_seconds() <= float(duration * 60) and datetime.now() < end:
      cursor.callproc('show_questions', [exam_id])
      for result in cursor.stored_results():
        exams_question = result.fetchall()
      for question in exams_question:
        print(f'{question[1]},{question[2]},{question[3]},{question[4]},{question[5]}')
        s_saw_question = datetime.now()
        print("YOUR anwser: ")
        answer = input()
        answerd_question = datetime.now()
        if (answerd_question - s_saw_question).total_seconds() <= float(duration * 60):
          cursor.execute(f"select submit_answer({question[0]},{username},'{answer}',{exam_id},{course});")
          if cursor.fetchall()[0][0] == 1:
            connection.commit()
            print('Answer submited')
          else:
            print('something went wrong')
        else:
          calculate_exam(username, exam_id)
          print('The answering time passed exam duration')
      break
  else:
    print('more than once attended')


def calculate_exam(username, exam_id):
  cursor.execute(f'select cal_exam_grade({username}, {exam_id})')
  grade = cursor.fetchall()[0][0]
  connection.commit()
  print(f'total score {grade}')
  cursor.callproc('review_exam', [username, exam_id])
  for result in cursor.stored_results():
    exams = result.fetchall()
  print('Review of exam')
  if len(exams) == 0:
    print('not such an exam')
  else:
    print(exams)


def upload_homework(username):
  print('choose the course you want to upload homework:')
  results = show_courses('Student', username)
  selected_course = int(input())
  selected_course = results[selected_course - 1][0]
  cursor.callproc('student_all_homeworks_of_course', [selected_course])
  for result in cursor.stored_results():
    hws = result.fetchall()
  print(f'HOMEWORKS of course {selected_course} : ')
  if len(hws) != 0:
    for hw in hws:
      print(hw[1], end=' | ')
    print()
    print('please choose the homework you want to answer: ')
    choose_hw = int(input())
    hw_id = hws[choose_hw - 1][0]
    cursor.execute(f"SELECT get_hw_deadline('{hw_id}');")
    temp = cursor.fetchall()
    if temp[0][0] > datetime.now():
      sos = f"select time_update('{datetime.now()}','{hw_id}','{username}',{selected_course})"
      cursor.execute(sos)
      connection.commit()
      if cursor.fetchall()[0][0] == 1:
        print(f"HOMEWORK {hws[choose_hw - 1][1]}: ")
        cursor.callproc('show_homework', [selected_course, hw_id])
        for result in cursor.stored_results():
          hw_description = result.fetchall()
        if len(hw_description) != 0:
          for question in hw_description:
            print(f'ANSWER: {question[0]}')
            response = input()
            cursor.execute(
              f"SELECT upload('{username}','{hw_id}','{question[1]}','{response}','{datetime.now()}','{selected_course}')")
            connection.commit()
            if cursor.fetchall()[0][0] == 0:
              print('Time out')
              break
          print('HW finished!')
      else:
        print('update time failed')
    else:
      print('Deadline passed')
  else:
    print('no hws sets for this course')


def show_homework_upload(username):
  cursor.callproc('show_history_of_upload', [username])
  for result in cursor.stored_results():
    answered_homeworks = result.fetchall()
  if len(answered_homeworks) != 0:
    print(f'Student {username} homework status:')
    for exam in answered_homeworks:
      print(
        f"student_id : {exam[0]}, course_id: {exam[5]}, homework_id: {exam[1]}, question_id: {exam[2]}, answer: {exam[3]}")
  else:
    print('no homework submitted.')


def choose_exam_hw(username):
  exams, hws, course = exams_hw_prof(username)
  if len(exams) != 0:
    print('please choose an exam you want to see the result: ')
    choose_exam = int(input())
    if choose_exam != -1:
      print(exams[choose_exam-1][0])
      exams_id = exams[choose_exam - 1][0]
      cursor.callproc('get_all_exams_answers_prof', [course, exams_id])
      for result in cursor.stored_results():
        exams = result.fetchall()
      if len(exams) != 0:
        for exam in exams:
          print(f"student_id : {exam[0]}, question_id: {exam[1]}, user_answer: {exam[2]}, score: {exam[3]}")
      print()

  if len(hws) != 0:
    print('please choose the homework you want to see the result: ')
    choose_hw = int(input())
    if choose_hw != -1:
      hws_id = hws[choose_hw - 1][0]
      cursor.callproc('get_all_homeworks_asnwers_prof', [course, hws_id])
      for result in cursor.stored_results():
        exams = result.fetchall()
      if len(exams) != 0:
        for exam in exams:
          print(f"student_id : {exam[0]}, time: {exam[3]}, grade: {exam[4]}, question_id: {exam[1]}, answer: {exam[2]}")
      print()


def exams_hw_student(username):
  print('choose the course you want to see exams and homeworks for:')
  results = show_courses('Student', username)
  selected_course = int(input())
  selected_course = results[selected_course - 1][0]
  cursor.callproc('student_all_exam_of_course', [selected_course])
  for result in cursor.stored_results():
    exams = result.fetchall()
  print(f'EXAMS of course {selected_course}: ')
  if len(exams) != 0:
    for exam in exams:
      print(exam[1], end=' | ')
    print()
  else:
    print('no exam sets for this course')

  cursor.callproc('student_all_homeworks_of_course', [selected_course])
  for result in cursor.stored_results():
    hws = result.fetchall()
  print(f'HOMEWORKS of course {selected_course} : ')
  if len(hws) != 0:
    for hw in hws:
      print(hw[1], end=' | ')
    print()
  else:
    print('no hws sets for this course')
  print('-------------------')
  return exams, hws


def exams_hw_prof(username):
  print('choose the course you want to see exams and homeworks for:')
  results = show_courses('Professor', username)
  selected_course = int(input())
  selected_course = results[selected_course - 1][0]
  cursor.callproc('prof_all_exam_of_course', [selected_course])
  for result in cursor.stored_results():
    exams = result.fetchall()
  print(f'EXAMS of course {selected_course}: ')
  if len(exams) != 0:
    for exam in exams:
      print(exam[1], end=' | ')
    print()
  else:
    print('no exams set for this course')

  cursor.callproc('prof_all_homeworks_of_course', [selected_course])
  for result in cursor.stored_results():
    hws = result.fetchall()
  print(f'HOMEWORKS of course {selected_course} : ')
  if len(hws) != 0:
    for hw in hws:
      print(hw[1], end=' | ')
    print()
  else:
    print('no hws set for this course')
  print('-------------------')
  return exams, hws, selected_course


def create_homework(username):
  print('choose the course you want to make homework for:')
  results = show_courses('Professor', username)
  selected_course = int(input())
  selected_course = results[selected_course - 1][0]
  print('homework name: ')
  name = input()
  print('Deadline:')
  deadline = input()
  temp = f"Select create_homework('{name}','{selected_course}','{deadline}');"
  cursor.execute(temp)
  created = cursor.fetchall()
  connection.commit()
  hw_id = created[0][0]
  print(hw_id)
  print('Write down homework question:')
  questions = hw_questions()
  for question in questions:
    temp = f"select create_homework_question({hw_id},'{question[0]}','{question[1]}', {question[2]})"
    cursor.execute(temp)
    result = cursor.fetchall()
    if result[0][0] != 1:
      print('something went wrong')
      break
    connection.commit()
  print(f"homework '{name}' for '{selected_course}' CREATED!")


def hw_questions():
  questions = []
  while True:
    temp = []
    print('question:')
    question_description = input()
    temp.append(question_description)
    print('correct_answer:')
    correct_answer = input()
    temp.append(correct_answer)
    print('question_score: ')
    score = int(input())
    temp.append(score)
    print('to exit question mode enter -1:')
    questions.append(temp)
    if input() == '-1':
      break
  return questions


def create_exam(username):
  print('choose the course you want to make exam for: ')
  results = show_courses('Professor', username)
  selected_course = int(input())
  selected_course = results[selected_course - 1][0]
  print("name: ")
  name = input()
  # 2005-7-27 09:00:30.75
  print('start time: ')
  start_time = input()
  print('end time: ')
  end_time = input()
  print('exam_duration: ')
  exam_duration = int(input())
  temp = f"Select create_exam('{selected_course}','{name}','{start_time}','{end_time}', {exam_duration});"
  cursor.execute(temp)
  exam_id = cursor.fetchall()[0][0]
  connection.commit()
  print('list of test questions of exam :')
  questions = exam_questions()
  for question in questions:
    temp = cursor.execute(
      f"select create_question_exam('{question[0]}','{question[1]}','{question[2]}','{question[3]}','{question[4]}','{exam_id}','{question[5]}',{question[6]})")
    cursor.execute(temp)
    result = cursor.fetchall()
    if result[0][0] != 1:
      print('something went wrong')
      break
    connection.commit()
  print(f'exam {exam_id} for {selected_course} CREATED!')


def exam_questions():
  questions = []
  while True:
    temp = []
    print('question description: ')
    question_description = input()
    temp.append(question_description)
    print('options:')
    options = input().split(' ')
    for option in options:
      temp.append(option)
    print('correct answer: ')
    correct_answer = input()
    temp.append(correct_answer)
    print('question score: ')
    question_score = int(input())
    temp.append(question_score)
    print('to exit question mode enter -1:')
    questions.append(temp)
    if input() == '-1':
      print('list of questions made.')
      break
  return questions


def show_student_of_prof(username):
  print('please select one of your courses')
  results = show_courses('Professor', username)
  selected_course = int(input())
  selected_course = results[selected_course - 1][0]
  cursor.execute(
    f"select student_no from course natural join classroom where course.professor_no = '{username}' and course_id = '{selected_course}';")
  list_of_students = cursor.fetchall()
  print(f'List of student of course {selected_course}: ')
  for i in range(0, len(list_of_students)):
    print(f'{i + 1}) {list_of_students[i][0]}', end=' ')
    if i % 14 == 0 and i != 0:
      print()
  print()


def show_courses(role, username):
  if role == 'Student':
    temp = f"Select * from course natural join classroom where '{username}' =  classroom.student_no;"
  if role == 'Professor':
    temp = f"Select * from course where '{username}' = professor_no ;"
  cursor.execute(temp)
  results = cursor.fetchall()
  for i in range(0, len(results)):
    print(f'{i + 1}) course_id: {results[i][0]} , course name: {results[i][1]}, professor_no: {results[i][2]}')
  return results


def logout(username):
  temp = f"select logout('{username}');"
  cursor.execute(temp)
  if cursor.fetchall()[0][0] != 1:
    print('something went wrong')
  else:
    connection.commit()
    print('Logged out!')


def change_password(role, username, password):
  print('Enter new password:')
  new_pass = input()
  if role == 'Student':
    action_sql = f"SELECT change_student_password('{username}', '{password}', '{new_pass}');"

  if role == 'Professor':
    action_sql = f"SELECT change_professor_password('{username}', '{password}', '{new_pass}');"

  cursor.execute(action_sql)
  connection.commit()
  print('password changed successfully!')


try:
  connection = mysql.connector.connect(host='localhost',
                                       database='educational_managment_system',
                                       user='root',
                                       password='rojina12345')
  if connection.is_connected():
    db_Info = connection.get_server_info()
    print("Connected to MySQL Server version ", db_Info)
    cursor = connection.cursor(buffered=True)
    # load_tables()
    program_starts()

except Error as e:
  print("Error while connecting to MySQL", e)
finally:
  if connection.is_connected():
    temp = f'UPDATE last_login set log_in = 0;'
    cursor.execute(temp)
    connection.commit()
    connection.close()
    print("MySQL connection is closed")
