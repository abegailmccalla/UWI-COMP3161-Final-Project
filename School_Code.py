# The University of the West Indies, Mona Campus
# FST COMP3161 Lab 2 Faker Code (Python)
# Abegail McCalla (620157646)

from faker import Faker
import random
import os
import sqlite3

fake = Faker()
fake.seed_instance(42)

# Lists to store generated data
admins = []
lecturers = []
students = []
users = []
courses = []
teaches = []
enrols = []
assignments = []
submits = []
course_forum_map = {}
threads = []
generates = []
creates = []
course_topic_map = {}
contents = []
events = []

# Generate SQL insert statements
with open('School_Database.sql', 'w') as file:
    file.write("\n-- The University of the West Indies, Mona Campus --")
    file.write("\n-- FST COMP3161 Final Project Database (SQL) --")
    file.write("\n-- Abegail McCalla (620157646)  --\n")

    file.write("\nDROP DATABASE IF EXISTS school;")
    file.write("\nCREATE DATABASE school;")
    file.write("\nUSE school;\n")

    # Create User Table
    file.write("\n-- Users --\n")
    file.write("CREATE TABLE Users (user_id INT AUTO_INCREMENT PRIMARY KEY, f_Name VARCHAR(30) NOT NULL, l_Name VARCHAR(30) NOT NULL, role VARCHAR(10) NOT NULL, password VARCHAR(200) NOT NULL);\n")
    file.write("ALTER TABLE Users AUTO_INCREMENT = 620000000;\n")
    # Generate fake data for users
    file.write("\n-- Insert Users --\n")
    i = 619999999
    for a in range(1, 21):
        i += 1
        f_name = fake.first_name()
        l_name = fake.last_name()
        pword = fake.lexify(text='?????') + fake.numerify(text='#####')
        users.append((i, f_name, l_name, "Admin", pword))
        file.write(f"INSERT INTO Users (f_Name, l_Name, role, password) VALUES ('{f_name}', '{l_name}', 'Admin', '{pword}');\n")
        admins.append(i)
    for l in range(1, 41):
        i += 1
        f_name = fake.first_name()
        l_name = fake.last_name()
        pword = fake.lexify(text='?????') + fake.numerify(text='#####')
        users.append((i, f_name, l_name, "Lecturer", pword))
        file.write(f"INSERT INTO Users (f_Name, l_Name, role, password) VALUES ('{f_name}', '{l_name}', 'Lecturer', '{pword}');\n")
        if (l <= 4):
            department = "Mathematics"
        elif (l >= 5 and l <= 8):
            department = "Science"
        elif (l >= 9 and l <= 12):
            department = "Engineering"
        elif (l >= 13 and l <= 16):
            department = "Computing"
        elif (l >= 17 and l <= 20):
            department = "Chemistry"
        elif (l >= 21 and l <= 24):
            department = "Physics"
        elif (l >= 25 and l <= 28):
            department = "Biology"
        elif (l >= 29 and l <= 32):
            department = "Geography"
        elif (l >= 33 and l <= 36):
            department = "Economics"
        elif (l >= 37 and l <= 40):
            department = "Psychology"
        lecturers.append((i, department))
    for s in range(1, 100001): #100001 
        i += 1
        f_name = fake.first_name()
        l_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=30)
        pword = fake.lexify(text='?????') + fake.numerify(text='#####')
        users.append((i, f_name, l_name, "Student", pword))
        file.write(f"INSERT INTO Users (f_Name, l_Name, role, password) VALUES ('{f_name}', '{l_name}', 'Student', '{pword}');\n")
        students.append((i, dob))
    
    # Create Admin Table
    file.write("\n-- Admin --\n")
    file.write("CREATE TABLE Admin (Admin_Id INT PRIMARY KEY, FOREIGN KEY (Admin_Id) REFERENCES Users(user_id) ON DELETE CASCADE);\n")
    # Generate fake data for admins
    file.write("\n-- Insert Admin --\n")
    for a in admins:
        file.write(f"INSERT INTO Admin (Admin_Id) VALUES ({a});\n")

    # Create Lecturer Table
    file.write("\n-- Lecturer --\n")
    file.write("CREATE TABLE Lecturer (Lect_Id INT PRIMARY KEY, Department VARCHAR(30), FOREIGN KEY (Lect_Id) REFERENCES Users(user_id) ON DELETE CASCADE);\n")
    # Generate fake data for Lecturer
    for l in lecturers:
        file.write(f"INSERT INTO Lecturer (Lect_Id, Department) VALUES ({l[0]}, '{l[1]}');\n")

    # Create Student Table
    file.write("\n-- Student --\n")
    file.write("CREATE TABLE Student (Std_Id INT PRIMARY KEY, DOB DATE, FOREIGN KEY (Std_Id) REFERENCES Users(user_id) ON DELETE CASCADE);\n")
    # Generate fake data for Student
    for s in students:
        file.write(f"INSERT INTO Student (Std_Id, DOB) VALUES ({s[0]}, '{s[1]}');\n")
    
    # Create Course Table
    file.write("\n-- Course --\n")
    file.write("CREATE TABLE Course (Course_Id VARCHAR(255) PRIMARY KEY, C_Title VARCHAR(255), Admin_Id INT, FOREIGN KEY (Admin_Id) REFERENCES Admin(Admin_Id) ON DELETE CASCADE);\n")
    # Generate fake data for courses   
    file.write("\n-- Insert Course\n")
    for c in range(1, 201):
        course_id = fake.lexify(text='????') + '-' + fake.numerify(text='####')
        c_title = fake.word()
        courses.append((course_id, c_title))
    course_ids = [cids[0] for cids in courses]
    i = 0
    for ads in admins:
        for cl in range(i, len(course_ids), 10):
            classes = course_ids[cl:cl + 10] #[cs[0] for cs in courses[cl:cl + clen]]
            creates.append((ads, classes)) 
            i = cl + 10
            break
    for c in courses:
        for ads in creates:
            if c[0] in ads[1]:
                c = c + (ads[0],)
                file.write(f"INSERT INTO Course (Course_Id, C_Title, Admin_Id) VALUES ('{c[0]}', '{c[1]}', {ads[0]});\n")
                break
 
    # Create Teaches Table
    file.write("\n-- Teaches --\n")
    file.write("CREATE TABLE Teaches (Lect_Id INT, Course_Id VARCHAR(255), PRIMARY KEY (Lect_Id, Course_Id), FOREIGN KEY (Lect_Id) REFERENCES Lecturer(Lect_Id), FOREIGN KEY (Course_Id) REFERENCES Course(Course_Id) ON DELETE CASCADE);\n")
    # Generate fake data for Teaches                                       
    file.write("\n-- Insert Teaches --\n")
    i = 0
    clen = 5
    for l in lecturers:
        for cl in range(i, len(courses), clen):
            classes = courses[cl:cl + clen] #[cs[0] for cs in courses[cl:cl + clen]]
            teaches.append((l[0], classes)) #l[0]
            i = cl + clen
            break
    for t in teaches:
        for c in t[1]:
            file.write(f"INSERT INTO Teaches (Lect_Id, Course_Id) VALUES ({t[0]}, '{c[0]}');\n")
    
    # Create Assignments Table
    file.write("\n-- Assignment --\n")
    file.write("CREATE TABLE Assignment (Assign_Id INT AUTO_INCREMENT PRIMARY KEY, Course_Id VARCHAR(255), Assign_Title VARCHAR(255), FOREIGN KEY (Course_Id) REFERENCES Course(Course_Id) ON DELETE CASCADE);\n")
    file.write("ALTER TABLE Assignment AUTO_INCREMENT = 1;\n")
    # Generate fake data for Assignment
    file.write("\n-- Insert Assignment --\n")
    aid = 0
    a_num = 0
    a_id = 0
    for c in courses:
        c_id = c[0]
        for c1 in range(0, 3):
            a_id += 1
            a_title = fake.sentence(nb_words=3)
            assignments.append((a_id, c_id, a_title))
            file.write(f"INSERT INTO Assignment (Course_Id, Assign_Title) VALUES ('{c_id}', '{a_title}');\n")

    # Create Enrol Table
    file.write("\n-- Enrols --\n")
    file.write("CREATE TABLE Enrols (Std_Id INT, Course_Id VARCHAR(255), Grade INT DEFAULT NULL, PRIMARY KEY (Std_Id, Course_Id), FOREIGN KEY (Std_Id) REFERENCES Student(Std_Id), FOREIGN KEY (Course_Id) REFERENCES Course(Course_Id) ON DELETE CASCADE);\n")
    # Generate fake data for Assignment
    stds = []
    cenrol = []
    i = 0
    for c in range(0, 200):
        for s in range(i, 100000, 500): #100000, 500
            stds = [st[0] for st in students[s:s + 500]] #500
            cenrol.append((courses[c][0], stds))
            i = s + 500 #500
            break
    for c in cenrol:
        for s in c[1]:
            enrols.append((s, [c[0]])) #(s, [(c[0])])
    stu_5_lst = [en for en in enrols[0: 500]] #500
    for s in stu_5_lst: 
        for c in range(0, 4):
            crse = random.choice(courses)
            while crse[0] in s[1]:
                crse = random.choice(courses)
            s[1].append(crse[0])
    stu_3_lst = [en for en in enrols[500:]] #500
    for s in stu_3_lst: 
        for c in range(0, 2):
            crse = random.choice(courses)
            while crse[0] in s[1]:
                crse = random.choice(courses)
            s[1].append(crse[0])
    enrols = stu_5_lst + stu_3_lst

    # Create Student Submits Table
    file.write("\n-- Submits --\n")
    file.write("CREATE TABLE Submits (Std_Id INT, Assign_Id INT, Assign_grade INT DEFAULT NULL, submit_time DATE, submission VARCHAR(255), PRIMARY KEY (Std_Id, Assign_Id), FOREIGN KEY (Std_Id) REFERENCES Student(Std_Id), FOREIGN KEY (Assign_Id) REFERENCES Assignment(Assign_Id) ON DELETE CASCADE);\n")
    # Generate fake data for Submits
    file.write("\n-- Insert Submits --\n")
    c_idx = 0
    file_extensions = [".doc",  # Microsoft Word Document (legacy)
                       ".docx",  # Microsoft Word Open XML Document
                        ".odt",  # OpenDocument Text Document
                        ".rtf",  # Rich Text Format
                        ".txt",  # Plain Text File
                        ".wps",  # Microsoft Works Word Processor Document
                        ".pdf",  # Portable Document Format
                        ".xps",  # XML Paper Specification
                        ".fdf",  # Forms Data Format (used with PDF forms)
                        ".epub",  # Open eBook Format
                        ".oxps"  # OpenXPS Format
                        ]
    stu_assignments = []
    for e in enrols:
        std_id = e[0]
        for cse in e[1]:
            # Filter assignments for the course
            course_assignments = [ass for ass in assignments if ass[1] == cse] # Get exactly 3 assignments per course
            for ass in course_assignments:
                assign_id = ass[0]
                sub_time = fake.date_between(start_date="-30d", end_date="today") #sub_time = fake.date_of_birth(minimum_age=0, maximum_age=1)
                submis = "As_" + str(assign_id) + random.choice(file_extensions)
                grade = random.randint(0, 100)
                file.write(f"INSERT INTO Submits (Std_Id, Assign_Id, Assign_grade, submit_time, submission) VALUES ({std_id}, {assign_id}, {grade}, '{sub_time}', '{submis}');\n")
                submits.append((std_id, cse, assign_id, grade, sub_time, submis))
    
    # Generate fake data for Enrol
    file.write("\n-- Insert Enrols --\n")
    avgG = 0
    for e in enrols:
        st_id = e[0]
        for cse in e[1]:
            stu_cse_grades = [sub[3] for sub in submits if sub[0] == st_id and sub[1] == cse]
            avgG = int(sum(stu_cse_grades) / len(stu_cse_grades))
            file.write(f"INSERT INTO Enrols (Std_Id, Course_Id, Grade) VALUES ({st_id}, '{cse}', {avgG});\n")
    
    # Create Discussion_Forum Table
    file.write("\n-- Discussion_Forum --\n")
    file.write("CREATE TABLE Discussion_Forum (Forum_Id INT AUTO_INCREMENT PRIMARY KEY, Course_Id VARCHAR(255), Forum_Title VARCHAR(255), FOREIGN KEY (Course_Id) REFERENCES Course(Course_Id) ON DELETE CASCADE);\n")
    file.write("ALTER TABLE Discussion_Forum AUTO_INCREMENT = 1;\n")
    # Generate fake data for Discussion_Forum
    forum_id = 1
    course_ids = [cids[0] for cids in courses]
    for cid in course_ids:
        title = f"{fake.bs().capitalize()} Forum"
        file.write(f"INSERT INTO Discussion_Forum (Course_Id, Forum_Title) VALUES ('{cid}', '{title}');\n")
        course_forum_map[cid] = forum_id
        forum_id += 1
    
    # Create Discussion_Thread Table
    file.write("\n-- Discussion_Thread --\n")
    file.write("CREATE TABLE Discussion_Thread (Thread_Id INT AUTO_INCREMENT PRIMARY KEY, Forum_Id INT, Thread_Title VARCHAR(255), date Date, FOREIGN KEY (Forum_Id) REFERENCES Discussion_Forum(Forum_Id) ON DELETE CASCADE);\n")
    file.write("ALTER TABLE Discussion_Thread AUTO_INCREMENT = 1;\n")
    # Create Generates Table
    #file.write("\n-- Generates --\n")
    #file.write("CREATE TABLE Generates (Thread_Id INT PRIMARY KEY, Reply_T0_Thread_Id INT, Thread_Title VARCHAR(255), date Date, PRIMARY KEY (Thread_Id, Reply_T0_Thread_Id), FOREIGN KEY (Thread_Id) REFERENCES Discussion_Thread(Thread_Id));\n") 
    # Generate fake data for Discussion_Thread 
    poss_stu = []
    thread_id = 1
    for cid, fid in course_forum_map.items():
        num_threads = random.randint(2, 6)
        for e in enrols:
            if cid in e[1]:
                poss_stu.append(e[0])
        for _ in range(num_threads):
            sid = random.choice(poss_stu)
            title = f"{fake.bs().capitalize()} Thread"
            date = fake.date_between(start_date='-30d', end_date='today')
            file.write(f"INSERT INTO Discussion_Thread (Forum_Id, Thread_Title, date) VALUES ({fid}, '{title}', '{date}');\n")
            threads.append((thread_id, fid, title, date))
            #file.write(f"INSERT INTO Generates (Std_Id, Thread_Id, Thread_Title) VALUES ({sid}, {thread_id}, '{title}', '{date}');\n")
            #generates.append((sid, thread_id, title, date))
            thread_id += 1
    
    # Create Topic Table
    file.write("\n-- Topic --\n")
    file.write("CREATE TABLE Topic (Topic_Id INT AUTO_INCREMENT PRIMARY KEY, Course_Id VARCHAR(255), Topic_Title VARCHAR(255), FOREIGN KEY (Course_Id) REFERENCES Course(Course_Id) ON DELETE CASCADE);\n")
    file.write("ALTER TABLE Topic AUTO_INCREMENT = 1;\n")
    # Generate fake data for Topic
    topic_id = 1
    course_ids = [cids[0] for cids in courses]
    for cid in course_ids:
        num_topics = random.randint(2, 4)
        topic_ids = []
        for _ in range(num_topics):
            title = fake.catch_phrase().replace("'", "''")
            file.write(f"INSERT INTO Topic (Course_Id, Topic_Title) VALUES ('{cid}', '{title}');\n")
            topic_ids.append(topic_id)
            topic_id += 1
            course_topic_map[cid] = topic_ids
    
        # Create Content Table
    file.write("\n-- Content --\n")
    file.write("CREATE TABLE Content (Content_Id INT AUTO_INCREMENT PRIMARY KEY, Topic_Id INT, link VARCHAR(255), file VARCHAR(255), slide VARCHAR(255), FOREIGN KEY (Topic_Id) REFERENCES Topic(Topic_Id) ON DELETE CASCADE);\n")
    file.write("ALTER TABLE Content AUTO_INCREMENT = 1;\n")
    # Generate fake data for Content
    content_id = 1
    for topic_list in course_topic_map.values():
        for tid in topic_list:
            num_content = random.randint(1, 3)
            for _ in range(num_content):
                link = fake.url()
                fle = f"lecture_{content_id}.pdf"
                slide = f"slide_{content_id}.pptx"
                file.write(f"INSERT INTO Content (Topic_Id, link, file, slide) VALUES ({tid}, '{link}', '{fle}', '{slide}');\n")
                contents.append((content_id, tid, link, fle, slide))
                content_id += 1

    # Create Events Table
    file.write("\n-- Events --\n")
    file.write("CREATE TABLE Events (Event_Id INT AUTO_INCREMENT PRIMARY KEY, Course_Id VARCHAR(255), Start_Date DATE, End_Date DATE, Event_Title VARCHAR(255), FOREIGN KEY (Course_Id) REFERENCES Course(Course_Id) ON DELETE CASCADE);\n")
    file.write("ALTER TABLE Events AUTO_INCREMENT = 1;\n")
    # Generate fake data for Events
    event_id = 1
    course_ids = [cids[0] for cids in courses]
    for cid in course_ids:
        num_events = random.randint(1, 3)
        for _ in range(num_events):
            start_date = fake.date_between(start_date='-60d', end_date='+30d')
            end_date = fake.date_between(start_date=start_date, end_date='+30d')
            title = fake.catch_phrase().replace("'", "''")
            file.write(f"INSERT INTO Events (Course_Id, Start_Date, End_Date, Event_Title) VALUES ('{cid}', '{start_date}', '{end_date}', '{title}');\n")
            events.append((event_id, cid, start_date, end_date, title))
            event_id += 1
    
    file.write("\n-- DONE--\n")
