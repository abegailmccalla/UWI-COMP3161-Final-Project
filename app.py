from flask import Flask, redirect, request, flash, make_response,jsonify,render_template, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from urllib import response
import json
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# Connect to the MySQL database
# mysql.connector.connect(host="localhost", user="UWICOMP3161", password="UWICOMP3161", database="school")
# mysql.connector.connect(host="localhost", user="UWICOMP3161_Test", password="UWICOMP3161", database="school_test")
db = mysql.connector.connect(host="localhost", user="UWICOMP3161", password="UWICOMP3161", database="school")

@app.route('/')
def home():
 return render_template('school.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/lecturer')
def lecturer():
    return render_template('lecturer.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

################################################################################## FRONTEND DONE  ##########################################

#Register a user
@app.route('/register_user', methods=['POST'])
def add_user():
    try:
        cursor = db.cursor()
        data = request.form # request.get_json()
        first_name = data.get('fname')
        last_name = data.get('lname')
        role = data.get('role')
        password = data.get('password1')
        if role not in ['Student', 'Lecturer', 'Admin']:
            return make_response(jsonify({'error': 'invalid role'}), 400)
        # Insert into user table
        cursor.execute("""
            INSERT INTO Users (f_Name, l_Name, role, password)
            VALUES (%s, %s, %s, %s)
        """, (first_name, last_name, role, password))
        #Get id of last user entered
        user_id = cursor.lastrowid
        if role == 'Student':
            dob = data.get("DOB")
            if not dob:
                return make_response(jsonify({'error': 'DOB is required for Student'}), 400)
            cursor.execute("INSERT INTO Student (Std_Id,DOB) VALUES (%s,%s)", (user_id,dob))
        elif role == 'Lecturer':
            department = data.get("department")
            if not department:
                return make_response(jsonify({'error': 'Department is required for Lecturer'}), 400)
            cursor.execute("INSERT INTO Lecturer (Lect_Id,Department) VALUES (%s,%s)", (user_id,department))
        elif role == 'Admin':
            cursor.execute("INSERT INTO Admin  (Admin_Id) VALUES (%s)", (user_id,))
        db.commit()
        return make_response(jsonify({'message': f"{role} added successfully, user ID is {user_id}"}), 201)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

# Login by a user 
@app.route('/login', methods=['POST'])
def login():
    try:
        cursor = db.cursor(dictionary=True)
        data = request.form
        userID = data.get('userID')
        password = data.get('password2')
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (userID,))
        user = cursor.fetchone()
        if user is None:
            return make_response(jsonify({'error': 'user does not exist'}), 400)
        # Compare password with the stored hashed password
        if user['password'] == password:
            #return make_response(jsonify({'message': 'Login successful'}), 200)
            if user['role'] == 'Admin':
                return jsonify({'redirect': url_for('admin')}) #redirect(url_for('admin'))
            elif user['role'] == 'Lecturer':
                return jsonify({'redirect': url_for('lecturer')}) #redirect(url_for('lecturer'))
            elif user['role'] == 'Student':
                return jsonify({'redirect': url_for('student')}) #redirect(url_for('student')) 
        else:
            return make_response(jsonify({'error': 'incorrect password'}), 401)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

#Create a course by Admin
@app.route('/create_course', methods=['POST'])
def newCourse():
    try:
        cursor = db.cursor()
        data = request.form
        courseID = data["courseID"]
        title = data["title"]
        adminID = data["adminID"] # when doing front end get session id
        # Check if the adminID exists in the admin table
        cursor.execute("SELECT * FROM Admin WHERE Admin_Id = %s", (adminID,))
        admin = cursor.fetchone()
        if not admin:
            return make_response(jsonify({'error': 'Unauthorized. Only admins can create a course.'}), 403)
        cursor.execute("""
            INSERT INTO Course (Course_Id, C_Title)
            VALUES (%s, %s)
        """, (courseID, title))
        cursor.execute("""
            INSERT INTO Creates (Admin_Id, Course_Id)
            VALUES (%s, %s)
        """, (adminID, courseID))
        db.commit()
        return make_response(jsonify({'message': f"Course {courseID} created successfully"}), 201)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

#Get all courses on the system
@app.route('/get_courses', methods=['GET'])
def get_all_courses():
    try:
        cursor = db.cursor(dictionary = True)
        cursor.execute("SELECT Course_Id, C_Title FROM Course")
        course_list = cursor.fetchall()
        return make_response(jsonify(course_list), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

#Get courses by Lecturer ID
@app.route('/get_course_lecturer/<int:id>', methods=['GET'])
def get_lecturer_courses(id):
    try:
       cursor = db.cursor(dictionary = True)
       cursor.execute("""SELECT c.Course_Id, c.C_Title 
                         FROM Teaches t
                      JOIN Course c ON c.Course_Id = t.Course_Id
                      WHERE t.Lect_Id = %s   
                      """,(id,))
       course_list = cursor.fetchall()
       return make_response(jsonify(course_list), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/get_course_student/<int:id>', methods=['GET'])
def get_student_courses(id):
    try:
       cursor = db.cursor(dictionary = True)
       # --- Get Lecturer for the course ---
       cursor.execute("""SELECT c.Course_Id, c.C_Title 
                      FROM Enrols e
                      JOIN Course c ON e.Course_Id = c.Course_Id
                      WHERE e.Std_Id = %s"""
                      ,(id,))
       course_list = cursor.fetchall()
       return make_response(jsonify(course_list), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

#Register a Student for a course
@app.route('/register_course_student', methods=['POST'])
def register():
    try:
        cursor = db.cursor()
        data = request.form
        student_id = data['SID'] #get from session in frontend
        course_id = data['CID']
        #Check if course exists
        cursor.execute("SELECT * FROM Course WHERE Course_Id = %s", (course_id,))
        course = cursor.fetchone()
        if not course:
            return make_response(jsonify({'error': 'Course not found'}), 404)
        # Check if student exists
        cursor.execute("SELECT * FROM Student WHERE Std_Id = %s", (student_id,))
        student = cursor.fetchone()
        if not student:
            return make_response(jsonify({'error': 'Student not found'}), 404)
        # Check if already enrolled
        cursor.execute("""
            SELECT * FROM Enrols WHERE Std_Id = %s AND Course_Id = %s
        """, (student_id, course_id))
        if cursor.fetchone():
            return make_response(jsonify({'error': 'Student already enrolled in this course'}), 400)
        # Check if student does max of 6 course
        cursor.execute(""" SELECT COUNT(Std_id)
                           FROM Enrols
                           WHERE Std_Id = %s""" ,(student_id,))
        count = cursor.fetchone()[0]
        if count >= 6:
            return make_response(jsonify({'error': 'Student already does 6 courses.'}), 400)
        else:
            # Register student for course
            cursor.execute("""
                INSERT INTO Enrols (Std_Id, Course_Id)
                VALUES (%s, %s)
            """, (student_id, course_id))
            db.commit()
        return make_response(jsonify({'message': f"Student registered successfully for {course_id}"}), 201)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

#Assign a Lecturer to teach a course (Remember that each lecturer already teaches 5 when you are testing)
@app.route('/register_course_lecturer', methods=['POST'])
def teach():
    try:
        cursor = db.cursor()
        data = request.form #get_json()
        lecturer_id = data['LID'] #get from session in frontend
        course_id = data['CID']
        #Check if course exists
        cursor.execute("SELECT * FROM Course WHERE Course_Id = %s", (course_id,))
        course = cursor.fetchone()
        if not course:
            return make_response(jsonify({'error': 'Course not found'}), 404)
        # Check if lecturer exists
        cursor.execute("SELECT * FROM Lecturer WHERE Lect_Id = %s", (lecturer_id,))
        lecturer = cursor.fetchone()
        if not lecturer:
            return make_response(jsonify({'error': 'Lecturer not found'}), 404)
        # Check if already teaches
        cursor.execute("""
            SELECT * FROM Teaches WHERE Lect_Id = %s AND Course_Id = %s
        """, (lecturer_id, course_id))
        if cursor.fetchone():
            return make_response(jsonify({'error': 'Lecturer already teaches in this course'}), 400)
        # Check if lecturer teaches max of 5 course
        cursor.execute(""" SELECT COUNT(Lect_Id)
                           FROM Teaches
                           WHERE Lect_Id = %s""" ,(lecturer_id,))
        count = cursor.fetchone()[0]
        if count >= 5:
            return make_response(jsonify({'error': 'Lecturer already teaches 5 courses.'}), 400)
        else:
            # Check if course already has a lecturer
            cursor.execute(
                """SELECT Lect_Id FROM Teaches WHERE Course_ID = %s"""
            , (course_id,))
            preExisting_lecturer = cursor.fetchone()
            if preExisting_lecturer:
                # Reassign lecturer for course
                cursor.execute("""
                    UPDATE Teaches
                    SET Lect_Id = %s
                    WHERE Course_Id = %s
                """, (lecturer_id, course_id))
            else:
                # Register lecturer for course
                cursor.execute("""
                    INSERT INTO Teaches (Lect_Id, Course_Id)
                    VALUES (%s, %s)
                """, (lecturer_id, course_id))
            db.commit()
        return make_response(jsonify({'message': f"Lecturer assigned successfully to course {course_id}"}), 201)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/Enrols/<Course_Id>', methods=['GET'])
def get_members_by_Course_Id(Course_Id):
    try:
        cursor = db.cursor()
        members = []
        # --- Get Lecturer for the course ---
        cursor.execute("""
            SELECT u.user_id, u.f_Name, u.l_Name, u.role
            FROM Teaches t
            JOIN Lecturer l ON t.Lect_Id = l.Lect_Id
            JOIN Users u ON u.user_id = l.Lect_Id
            WHERE t.Course_Id = %s
            LIMIT 1;
        """, (Course_Id,))
        lecturer = cursor.fetchone()
        if lecturer:
            user_id, f_name, l_name, role = lecturer
            members.append({
                "userId": user_id,
                "f_Name": f_name,
                "l_Name": l_name,
                "role": role
            })
        # --- Get Students for the course ---
        cursor.execute("""
            SELECT u.user_id, u.f_Name, u.l_Name, u.role
            FROM Enrols e
            JOIN Student s ON e.Std_Id = s.Std_Id
            JOIN Users u ON u.user_id = s.Std_Id
            WHERE e.Course_Id = %s;
        """, (Course_Id,))
        students = cursor.fetchall()
        for id, f_name, l_name, role in students:
            members.append({
                "userId": id,
                "f_Name": f_name,
                "l_Name": l_name,
                "role": role
            })
        return make_response(jsonify(members), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()
   
@app.route('/Calendar_Events/<Course_Id>', methods = ['GET'])
def get_events_by_course_Id(Course_Id):
    try: 
        cursor = db.cursor()
        cursor.execute ('SELECT Event_Id, Course_Id, Start_Date, End_Date, Event_Title FROM Events WHERE Course_Id =%s;',(Course_Id,))
        lst_event = []
        for eventId, courseId, start, end, event_title in cursor:
            event ={}
            event['Event_Id'] = eventId
            event['Course_Id'] = courseId
            event['Start_Date'] = start
            event['End_Date'] = end
            event['Event_Title'] = event_title
            lst_event.append(event)
        return make_response(jsonify(lst_event), 200)
    except Error as e:
        return make_response(jsonify({'error':str(e)}),400)
    finally:
        cursor.close()
    
@app.route('/Calendar_Events/<Student_Id>/<Date>', methods = ['GET'])
def get_events_by_student_id(Student_Id, Date):
    try: 
        cursor = db.cursor()
        cursor.execute(""" 
            SELECT cal.Event_Id, cal.Course_Id, c.C_Title, cal.Start_Date, cal.End_Date, cal.Event_Title
            FROM Events cal
            JOIN Course c ON cal.Course_Id = c.Course_Id
            JOIN Enrols e ON cal.Course_Id = e.Course_Id 
            WHERE e.Std_Id = %s AND (cal.Start_Date = %s OR cal.End_Date = %s)
            ORDER BY cal.Start_Date ASC;         
        """,(Student_Id, Date, Date))
        events = []
        for eventId, course_id, course_title, start_date, end_date, event_title in cursor:
            s_event = {}
            s_event['Event_Id'] = eventId
            s_event['Course_Id'] = course_id
            s_event['Course_Title'] = course_title
            s_event['Start_Date'] = start_date
            s_event['End_Date'] = end_date
            s_event['Event_Title'] = event_title
            events.append(s_event)
        return make_response(events, 200)
    except Error as e:
        return make_response({'error':str(e)},400)
    finally:
        cursor.close()
    
@app.route('/add_event', methods = ['POST'])
def add_event():
    try: 
        cursor = db.cursor()
        content = request.form #get_json()
        id = content['courseID']
        start = content['startDate']
        end = content['endDate']
        title = content['eventTitle']
        # Check if course exists
        cursor.execute("SELECT * FROM Course WHERE Course_Id = %s", (id,))
        course = cursor.fetchone()
        if not course:
            return make_response(jsonify({'error': 'Course not found'}), 404)
        # Check if event already exists 
        cursor.execute("SELECT * FROM Events WHERE Start_Date = %s AND End_Date = %s AND Course_Id = %s", (start, end, id))
        event = cursor.fetchone()
        if event:
            return make_response(jsonify({'error': 'Event already exists'}), 400)
        cursor.execute("INSERT INTO Events (Start_Date, End_Date, Course_Id, Event_Title) Values (%s, %s, %s, %s);",(start,end,id,title))
        db.commit()
        return make_response(jsonify({'message': f"'{title}' added for course {id}"}), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()
    
@app.route('/forums/<Course_Id>', methods = ['GET'])
def get_forums(Course_Id):
    try: 
        cursor = db.cursor()
         # Check if course exists
        cursor.execute("SELECT 1 FROM Course WHERE Course_Id = %s", (Course_Id,))
        if cursor.fetchone() is None:
            return make_response({'error': f"Course '{Course_Id}' does not exist"}, 404)
        cursor.execute ("SELECT * FROM Discussion_Forum WHERE Course_Id = %s;",(Course_Id,))
        forums = []
        for id, c_id, title in cursor:
            forum = {}
            forum["forumID"] = id
            forum["courseID"] = c_id
            forum["title"] = title
            forums.append(forum)
        return make_response(forums, 200)
    except Error as e:
        return make_response({'error':str(e)},400)
    finally:
        cursor.close()
    
@app.route('/add_forum', methods=['POST'])
def add_forum():
    try:
        cursor = db.cursor()
        data = request.form
        course_id = data['forumCourseID']
        title = data['forumTitle']
        # Check if course exists
        cursor.execute("SELECT 1 FROM Course WHERE Course_Id = %s", (course_id,))
        if cursor.fetchone() is None:
            return make_response(jsonify({'error': f"Course '{course_id}' does not exist"}), 404)
        # Insert new forum
        cursor.execute("""
            INSERT INTO Discussion_Forum (Course_Id, Forum_Title)
            VALUES (%s, %s)
        """, (course_id, title))
        db.commit()
        return make_response(jsonify({'message': f"'{title}' Added Successfully"}), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()

@app.route('/see_threads/<int:Forum_Id>', methods=['GET'])
def get_threads(Forum_Id):
    try:
       cursor = db.cursor(dictionary = True)
       cursor.execute("SELECT * FROM Discussion_Thread WHERE Forum_Id = %s;", (Forum_Id,))
       forums = cursor.fetchall()
       return make_response(jsonify(forums), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()
    
@app.route('/create_threads', methods = ['POST'])
def create_threads():
    try: 
        cursor = db.cursor()
        data = request.form # request.get_json()
        FID = data.get('FID')
        CTtitle = data.get('CTtitle')
        CTdte = data.get('CTdte')
        cursor.execute("SELECT 1 FROM Discussion_Forum WHERE Forum_Id = %s", (FID,))
        if cursor.fetchone() is None:
            return make_response({'error': f"Forum '{FID}' does not exist"}, 404)
        cursor.execute("""
            INSERT INTO Discussion_Thread (Forum_Id, Thread_Title, date)
            VALUES (%s, %s, %s)
        """, (FID, CTtitle, CTdte))
        db.commit()
        return make_response(jsonify({'message': "Thread added successfully"}), 201)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route('/reply_threads', methods = ['POST'])
def reply_threads():
    try: 
        cursor = db.cursor()
        data = request.form # request.get_json()
        TID = data.get('TID')
        RTtitle = data.get('RTtitle')
        RTdte = data.get('RTdte')
        cursor.execute("SELECT Forum_Id FROM Discussion_Thread WHERE Thread_Id = %s", (TID,))
        result = cursor.fetchone()
        if result is None:
            return make_response({'error': f"Thread '{TID}' does not exist"}, 404)
        FID = result[0]  # Extract the Forum_Id from the query result
        ReplyTitle = f"Reply To Thread {TID}: {RTtitle}"
        cursor.execute("""
            INSERT INTO Discussion_Thread (Forum_Id, Thread_Title, date)
            VALUES (%s, %s, %s)
        """, (FID, ReplyTitle, RTdte))
        db.commit()
        return make_response(jsonify({'message': "Thread added successfully"}), 201)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 500)  
    finally:
        cursor.close()

@app.route('/add_topic', methods = ['POST'])
def add_topic():
    try: 
        cursor = db.cursor()
        content= request.form
        course_id = content.get("contentCourseID")
        topic_title = content.get("topicTitle")
        cursor.execute("SELECT * FROM Course WHERE Course_Id = %s", (course_id,))
        course = cursor.fetchone() 
        if not course:
            return make_response(jsonify({'error': 'Course not found'}), 404)
        # Insert into Topic
        cursor.execute("INSERT INTO Topic (Course_Id, Topic_Title) VALUES (%s, %s);", (course_id, topic_title))
        topic_id = cursor.lastrowid
        db.commit()
        return make_response(jsonify({'message': f"Topic {topic_id} Added"}), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()

@app.route('/add_content', methods = ['POST'])
def add_content():
    try: 
        cursor = db.cursor()
        content= request.form
        topic_id = content.get("topicID")
        cursor.execute("SELECT * FROM Topic WHERE Topic_Id = %s", (topic_id,))
        course = cursor.fetchone() 
        if not course:
            return make_response(jsonify({'error': 'Course not found'}), 404)
        link = content.get("link")
        file = content.get("file")
        slide = content.get("slide")
        # Insert into Content
        cursor.execute("""
        INSERT INTO Content (Topic_Id, link, file, slide)
        VALUES (%s, %s, %s, %s)
        """, (topic_id, link, file, slide))
        content_id = cursor.lastrowid
        db.commit()
        return make_response(jsonify({'message': f"Content {content_id} Added"}), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()

@app.route('/course_content/<course_id>', methods = ['GET'])
def get_course_content(course_id):
    try: 
        cursor = db.cursor()
         # Check if course exists
        cursor.execute("SELECT 1 FROM Course WHERE Course_Id = %s", (course_id,))
        if cursor.fetchone() is None:
            return make_response(jsonify({'error': f"Course '{course_id}' does not exist"}), 404)
        cursor.execute( """SELECT t.Topic_Id, t.Topic_Title, c.Content_Id, c.link, c.file, c.slide
                       FROM Content c
                       JOIN Topic t ON c.Topic_Id = t.Topic_Id
                       WHERE t.Course_Id = %s;
                       """, (course_id,))
        C_content = [] 
        for topic_id, topic_title, content_id, link, file, slide in cursor:
            content = {}
            content["topicId"] = topic_id
            content["topicTitle"] = topic_title
            content["contentId"] = content_id
            content["link"] = link
            content["file"] = file
            content["slide"] = slide
            C_content.append(content)
        return make_response(jsonify(C_content), 200)
    except Error as e:
        return make_response(jsonify({'error':str(e)}),400)
    finally:
        cursor.close()
    
@app.route("/add_assignment",methods=['POST'])
def add_Assigments():
    try:
        cursor = db.cursor()
        data = request.form
        c_id = data.get("AssCourseID")
        ass_title = data.get("AssTitle")
        cursor.execute("""INSERT INTO Assignment (Course_Id, Assign_Title)
            VALUES (%s, %s)""", (c_id, ass_title))
        db.commit()
        return make_response(jsonify({'message': 'Assignment submitted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route("/see_assignment/<course_id>",methods=['GET'])
def see_Assigments(course_id):
    try: 
        cursor = db.cursor()
         # Check if course exists
        cursor.execute("SELECT 1 FROM Course WHERE Course_Id = %s", (course_id,))
        if cursor.fetchone() is None:
            return make_response(jsonify({'error': f"Course '{course_id}' does not exist"}), 404)
        cursor.execute("""SELECT Assign_Id, Assign_Title 
                       FROM Assignment
                       WHERE Course_Id = %s""", (course_id,))
        C_assign = [] 
        for ass_id, ass_title in cursor:
            assign = {}
            assign["Assign_Id"] = ass_id
            assign["Assign_Title"] = ass_title
            C_assign.append(assign)
        return make_response(jsonify(C_assign), 200)
    except Error as e:
        return make_response(jsonify({'error':str(e)}),400)
    finally:
        cursor.close()

from datetime import datetime
#Submit assignments

@app.route("/submit_assignment",methods=['POST'])
def submit_Assigments():
     try:
        cursor = db.cursor()
        data = request.form
        student_id = data.get('subStdID')
        assign_id = data.get('subAssID')
        submit_time = datetime.now()
        submission_file = data.get('subFile')
        cursor.execute("""INSERT INTO Submits (Std_Id, Assign_Id, Assign_grade, submit_time, submission)
            VALUES (%s, %s, %s, %s, %s)""", (student_id, assign_id, None, submit_time, submission_file))
        db.commit()
        return make_response(jsonify({'message': f'Assignment submitted successfully on {submit_time}'}), 201)
     except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
     finally:
        cursor.close()

@app.route("/grade_assignment", methods=['POST'])
def grade_Assignments():
    try:
        cursor = db.cursor()
        data = request.form
        student_id = data.get("subStdID")
        assign_id = data.get("subAssID")
        grade = data.get("grade")
        cursor.execute("""UPDATE Submits SET Assign_grade = %s
                       WHERE Assign_Id = %s AND Std_Id = %s
                       """,(grade, assign_id, student_id))
        db.commit()
        if cursor.rowcount == 0:
            return make_response(jsonify({'error': 'Submission not found'}), 404)
        return make_response(jsonify({'message': 'Grade added successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()

@app.route("/student_course_average", methods=['POST'])
def get_student_average():
    try:
        cursor = db.cursor()
        data = request.form
        student_id = data.get('Std_Id')
        course_id= data.get('Course_Id')
        cursor.execute("""
            SELECT a.Assign_Id, s.Assign_grade
            FROM Assignment a
            JOIN Submits s ON a.Assign_id = s.Assign_id
            WHERE a.Course_Id = %s AND s.Std_Id = %s AND s.Assign_grade IS NOT NULL
        """,(course_id, student_id))
        submissions = cursor.fetchall()
        if not submissions:
            return jsonify({'message': 'No graded assignments found'}), 404
        totalgrade = sum([submission[1] for submission in submissions])
        average = totalgrade / len(submissions)

        cursor.execute("SELECT 1 FROM Enrols WHERE Std_Id = %s AND Course_Id = %s", (student_id, course_id))
        if cursor.fetchone() is None:
            cursor.execute("""INSERT INTO Enrols (Std_Id, Course_Id, Grade)
            VALUES (%s, %s, %s)""", (student_id, course_id, int(average)))
            db.commit()
        else:
            cursor.execute("""UPDATE Enrols SET Grade = %s
                       WHERE Std_Id = %s AND Course_Id = %s
                       """,(int(average), student_id, course_id))
            db.commit()

        return make_response(jsonify({
            'student_id': student_id,
            'course_id': course_id,
            'average_grade': round(average, 2)
        }), 200)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()





####################################################### REPORTS ###########################


# Route to get courses with 50+ students
@app.route('/reports_courses_50plus', methods=['GET'])
def get_courses_50plus():
    try:
        cursor = db.cursor()
        # Query to retrieve courses with 50 plus students USING A VIEW
        cursor.execute("""SELECT c.Course_Id, c.C_Title, COUNT(e.Std_Id) AS Student_Count
                       FROM Enrols e
                       JOIN Course c ON e.Course_Id = c.Course_Id
                       GROUP BY c.Course_Id, c.C_Title
                       HAVING COUNT(e.Std_Id) >= 50
                       """)
        results = []
        for course_id, course_name, student_count in cursor:
            course = {}  # Dictionary to store courses
            course['courseId'] = course_id
            course['courseTitle'] = course_name
            course['studentCount'] = student_count
            results.append(course)
        return make_response(jsonify(results), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()

# Route to get students in 5+ courses
@app.route('/reports_students_5plus', methods=['GET'])
def get_students_5plus():
    try:
        cursor = db.cursor()
        # Query to retrieve students in 5 or more courses USING A VIEW
        cursor.execute("""SELECT e.Std_Id, u.f_Name, u.l_Name, COUNT(e.Course_Id) AS Course_Count
                       FROM Enrols e
                       JOIN Users u ON e.Std_Id = u.user_id
                       GROUP BY e.Std_Id
                       HAVING COUNT(e.Course_Id) >= 5
                       """)
        results = []
        for student_id, first_name, last_name, course_count in cursor:
            student = {}  # Dictionary to store students
            student['studentId'] = student_id
            student['firstName'] = first_name
            student['lastName'] = last_name
            student['courseCount'] = course_count
            results.append(student)
        return make_response(jsonify(results), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()

# Route to get lecturers that teach 3+ courses
@app.route('/reports_lecturers_3plus', methods=['GET'])
def get_lecturers_3plus():
    try:
        #db = mysql.connector.connect(host="localhost", user="UWICOMP3161_Test", password="UWICOMP3161", database="school_test")
        cursor = db.cursor()
        # Query to retrieve all lecturers that teach 3 or more courses USING A VIEW
        cursor.execute("""SELECT t.Lect_Id, u.f_Name, u.l_Name, COUNT(t.Course_Id) AS Course_Count
                       FROM Teaches t
                       JOIN Users u ON t.Lect_Id = u.user_id
                       GROUP BY t.Lect_Id
                       HAVING COUNT(t.Course_Id) >= 3
                       """)
        results = []
        for lecturer_id, first_name, last_name, course_count in cursor:
            lecturer = {}  # Dictionary to store lecturers
            lecturer['lectureId'] = lecturer_id
            lecturer['firstName'] = first_name
            lecturer['lastName'] = last_name
            lecturer['courseCount'] = course_count
            results.append(lecturer)
        return make_response(jsonify(results), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()
    
# Route to get top 10 most enrolled courses
@app.route('/reports_top10courses', methods=['GET'])
def get_top10_courses():
    try:
        #db = mysql.connector.connect(host="localhost", user="UWICOMP3161_Test", password="UWICOMP3161", database="school_test")
        cursor = db.cursor()
        # Query to retrieve top 10 most enrolled courses USING A VIEW
        cursor.execute("""SELECT c.Course_Id, c.C_Title, COUNT(e.Std_Id) AS Student_Count
                       FROM Enrols e
                       JOIN Course c ON e.Course_Id = c.Course_Id
                       GROUP BY c.Course_Id, c.C_Title
                       ORDER BY Student_Count DESC
                       LIMIT 10
                       """)
        results = []
        for course_id, course_name, student_count in cursor:
            course = {}  # Dictionary to store courses
            course['courseID'] = course_id
            course['courseTitle'] = course_name
            course['studentCount'] = student_count
            results.append(course)
        return make_response(jsonify(results), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()

# Route to get top 10 students based on average grades
@app.route('/reports_top10students', methods=['GET'])
def get_top10_students():
    try:
        #db = mysql.connector.connect(host="localhost", user="UWICOMP3161", password="UWICOMP3161", database="school")
        cursor = db.cursor()
        # Query to retrieve top 10 students with the highest averages USING A VIEW
        cursor.execute("""SELECT e.Std_Id, u.f_Name, u.l_Name, AVG(e.Grade) AS Overall_Grade
                       FROM Enrols e
                       JOIN Users u ON e.Std_Id = u.user_id
                       GROUP BY e.Std_Id, u.f_Name, u.l_Name
                       ORDER BY Overall_Grade DESC
                       LIMIT 10
                       """)
        results = []
        for student_id, first_name, last_name, averageGrade in cursor:
            student = {}  # Dictionary to store students
            student['studentId'] = student_id
            student['firstName'] = first_name
            student['lastName'] = last_name
            student['averageGrade'] = round(averageGrade, 2) if averageGrade is not None else 0
            results.append(student)
        return make_response(jsonify(results), 200)
    except Error as e:
        return make_response(jsonify({'error': str(e)}), 400)
    finally:
        cursor.close()
        
################################################################################## FRONTEND DONE ^ ########################################## 


# if __name__ == '__main__':
#     app.run(port=6000)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
