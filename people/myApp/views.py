from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
import csv

def home(request):
    outputStudents = []
    outputProfessors = []
    outputcounties = []
    outputCOVID = []
    outputOfQuery1 = []
    outputOfQuery2 = []
    outputOfQuery3 = []
    outputOfQuery4 = []
    outputOfQuery5 = []

    with connection.cursor() as cursor:
        # Print Values
        sqlQueryStudents = "SELECT studentID, name, score, county FROM Students;"
        cursor.execute(sqlQueryStudents)
        fetchResultStudents = cursor.fetchall()

        sqlQueryProfessors = "SELECT facultyID, name, age, county FROM Professors;"
        cursor.execute(sqlQueryProfessors)
        fetchResultProfessors = cursor.fetchall()

        sqlQuerycounties = "SELECT countyName, population, city FROM counties;"
        cursor.execute(sqlQuerycounties)
        fetchResultcounties = cursor.fetchall()

        sqlQueryCOVID = "SELECT patientID, city FROM COVID;"
        cursor.execute(sqlQueryCOVID)
        fetchResultCOVID = cursor.fetchall()

        # Print Queries
        sqlQuery1 = "SELECT county, ROUND(AVG(score),4) FROM students GROUP BY county ORDER BY county ASC;"
        cursor.execute(sqlQuery1)
        fetchResultQuery1 = cursor.fetchall()

        sqlQuery2 = "SELECT city, ROUND(AVG(score),4) \
                     FROM students,counties\
                     WHERE students.county=counties.countyName\
                     GROUP BY city \
                     ORDER BY city ASC"
        cursor.execute(sqlQuery2)
        fetchResultQuery2 = cursor.fetchall()

        sqlQuery3 = "SELECT p1.name, s1.name \
                     FROM professors p1, students s1\
                     WHERE p1.county = s1.county \
                     AND p1.age >= (SELECT MAX(age) FROM professors p2 \
                                    WHERE p2.county=p1.county \
                                    GROUP BY (county)) \
                     AND s1.score >= (SELECT MAX(score) FROM students s2 \
                                      WHERE s2.county=s1.county \
                                      GROUP BY (county)) \
                     ORDER BY (p1.county);"
        cursor.execute(sqlQuery3)
        fetchResultQuery3 = cursor.fetchall()

        sqlQuery4 = "SELECT p1.name, s1.name \
                    FROM \
                    (SELECT name, age, city \
                    FROM professors, counties c1 \
                    WHERE county=countyName \
                    AND age = (SELECT MAX(age) \
                                FROM professors JOIN counties ON county=countyName \
                                WHERE city=c1.city \
                                GROUP BY city) \
                                ORDER BY city) p1, \
                    (SELECT name, score, city \
                    FROM students, counties c1 \
                    WHERE county=countyName \
                    AND score = (SELECT MAX(score) \
                                FROM students JOIN counties ON county=countyName \
                                WHERE city=c1.city \
                                GROUP BY city) \
                                ORDER BY city) s1 \
                    WHERE p1.city = s1.city \
                    ORDER BY p1.city;"

        cursor.execute(sqlQuery4)
        fetchResultQuery4 = cursor.fetchall()

        sqlQuery5 = "SELECT name, city \
                    FROM students JOIN counties ON county=countyName \
                    WHERE city IN  \
                    (SELECT top3.city \
                    FROM( \
                    SELECT numC.city, (patients/populations) AS Ratio \
                    FROM  \
                    (SELECT city, COUNT(patientID) AS patients \
                    FROM COVID \
                    GROUP BY city) numC, \
                    (SELECT city, SUM(population) AS populations \
                    FROM counties \
                    GROUP BY city) numP \
                    WHERE numC.city=numP.city \
                    ORDER BY Ratio DESC \
                    LIMIT 3) top3) \
                    ORDER BY city DESC;"
        cursor.execute(sqlQuery5)
        fetchResultQuery5 = cursor.fetchall()

        connection.commit()
        connection.close()

        # Send Whole Values
        for temp in fetchResultStudents:
            eachRow = {'studentID' : temp[0], 'name' : temp[1], 'score' : temp[2], 'county' : temp[3]}
            outputStudents.append(eachRow)

        for temp in fetchResultProfessors:
            eachRow = {'facultyID' : temp[0], 'name' : temp[1], 'age' : temp[2], 'county' : temp[3]}
            outputProfessors.append(eachRow)

        for temp in fetchResultcounties:
            eachRow = {'countyName' : temp[0], 'population' : temp[1], 'city' : temp[2]}
            outputcounties.append(eachRow)

        for temp in fetchResultCOVID:
            eachRow = {'patientID' : temp[0], 'city' : temp[1]}
            outputCOVID.append(eachRow)

        # Send Query Values
        for temp in fetchResultQuery1:
            eachRow = {'countyName' : temp[0], 'averageScore' : temp[1]}
            outputOfQuery1.append(eachRow)

        for temp in fetchResultQuery2:
            eachRow = {'cityName' : temp[0], 'averageScore' : temp[1]}
            outputOfQuery2.append(eachRow)

        for temp in fetchResultQuery3:
            eachRow = {'professorName' : temp[0], 'studentName' : temp[1]}
            outputOfQuery3.append(eachRow)

        for temp in fetchResultQuery4:
            eachRow = {'professorName' : temp[0], 'studentName' : temp[1]}
            outputOfQuery4.append(eachRow)

        for temp in fetchResultQuery5:
            eachRow = {'studentName' : temp[0], 'cityName' : temp[1]}
            outputOfQuery5.append(eachRow)

    return render(request, 'myApp/home.html', 
    {"students" : outputStudents,
     "professors" : outputProfessors,
     "counties" : outputcounties,
     "COVID" : outputCOVID,
     "output1" : outputOfQuery1,
     "output2" : outputOfQuery2,
     "output3" : outputOfQuery3,
     "output4" : outputOfQuery4,
     "output5" : outputOfQuery5})

def addStudent(request):
    with open('./myApp/templates/myApp/students.csv','r') as f:
        reader = csv.reader(f)

        for c in reader:
            sql = "INSERT INTO students VALUES (%s, %s, %s, %s)"
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(c))
                connection.commit()
        connection.close()  

    return redirect('home')

def addProfessor(request):
    with open('./myApp/templates/myApp/professors.csv','r') as f:
        reader = csv.reader(f)

        for c in reader:    
            sql = "INSERT INTO professors VALUES (%s, %s, %s, %s)"
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(c))
                connection.commit()
        connection.close()  

    return redirect('home')

def addcounty(request):
    with open('./myApp/templates/myApp/counties.csv','r') as f:
        reader = csv.reader(f)

        for c in reader:    
            sql = "INSERT INTO counties VALUES (%s, %s, %s)"
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(c))
                connection.commit()
        connection.close() 

    return redirect('home')

def addCOVID(request):
    with open('./myApp/templates/myApp/COVID.csv','r') as f:
        reader = csv.reader(f)

        for c in reader:    
            sql = "INSERT INTO covid VALUES (%s, %s)"
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(c))
                connection.commit()
        connection.close() 
    return redirect('home')


