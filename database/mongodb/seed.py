"""
Seed MongoDB: create collections, indexes, and populate with data.
Based on database/sql/DDL.sql and database/sql/DML.sql.
"""

from pymongo import ASCENDING, IndexModel, MongoClient

MONGO_URI = "mongodb://admin:password@localhost:27017"
DB_NAME = "university"


def seed():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    client.drop_database(DB_NAME)
    _create_indexes(db)
    _insert_data(db)

    client.close()
    print("Seed complete.")


def _create_indexes(db):
    db.course.create_indexes(
        [
            IndexModel([("course_id", ASCENDING)], unique=True),
            IndexModel([("dept_name", ASCENDING)]),
        ]
    )
    db.student.create_indexes(
        [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("dept_name", ASCENDING)]),
        ]
    )
    db.student_enrollments.create_indexes(
        [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("dept_name", ASCENDING)]),
        ]
    )
    db.takes.create_indexes(
        [
            IndexModel(
                [
                    ("id", ASCENDING),
                    ("course_id", ASCENDING),
                    ("sec_id", ASCENDING),
                    ("semester", ASCENDING),
                    ("year", ASCENDING),
                ],
                unique=True,
            ),
        ]
    )


def _insert_data(db):
    courses = [
            {
                "course_id": "BIO-101",
                "title": "Intro. to Biology",
                "dept_name": "Biology",
                "credits": 4,
            },
            {
                "course_id": "BIO-301",
                "title": "Genetics",
                "dept_name": "Biology",
                "credits": 4,
            },
            {
                "course_id": "BIO-399",
                "title": "Computational Biology",
                "dept_name": "Biology",
                "credits": 3,
            },
            {
                "course_id": "CS-101",
                "title": "Intro. to Computer Science",
                "dept_name": "Comp. Sci.",
                "credits": 4,
            },
            {
                "course_id": "CS-190",
                "title": "Game Design",
                "dept_name": "Comp. Sci.",
                "credits": 4,
            },
            {
                "course_id": "CS-315",
                "title": "Robotics",
                "dept_name": "Comp. Sci.",
                "credits": 3,
            },
            {
                "course_id": "CS-319",
                "title": "Image Processing",
                "dept_name": "Comp. Sci.",
                "credits": 3,
            },
            {
                "course_id": "CS-347",
                "title": "Database System Concepts",
                "dept_name": "Comp. Sci.",
                "credits": 3,
            },
            {
                "course_id": "EE-181",
                "title": "Intro. to Digital Systems",
                "dept_name": "Elec. Eng.",
                "credits": 3,
            },
            {
                "course_id": "FIN-201",
                "title": "Investment Banking",
                "dept_name": "Finance",
                "credits": 3,
            },
            {
                "course_id": "HIS-351",
                "title": "World History",
                "dept_name": "History",
                "credits": 3,
            },
            {
                "course_id": "MU-199",
                "title": "Music Video Production",
                "dept_name": "Music",
                "credits": 3,
            },
            {
                "course_id": "PHY-101",
                "title": "Physical Principles",
                "dept_name": "Physics",
                "credits": 4,
            },
        ]
    db.course.insert_many(courses)
    students = [
            {
                "id": "00128",
                "name": "Zhang",
                "dept_name": "Comp. Sci.",
                "tot_cred": 102,
            },
            {
                "id": "12345",
                "name": "Shankar",
                "dept_name": "Comp. Sci.",
                "tot_cred": 32,
            },
            {"id": "19991", "name": "Brandt", "dept_name": "History", "tot_cred": 80},
            {"id": "23121", "name": "Chavez", "dept_name": "Finance", "tot_cred": 110},
            {"id": "44553", "name": "Peltier", "dept_name": "Physics", "tot_cred": 56},
            {"id": "45678", "name": "Levy", "dept_name": "Physics", "tot_cred": 46},
            {
                "id": "54321",
                "name": "Williams",
                "dept_name": "Comp. Sci.",
                "tot_cred": 54,
            },
            {"id": "55739", "name": "Sanchez", "dept_name": "Music", "tot_cred": 38},
            {"id": "70557", "name": "Snow", "dept_name": "Physics", "tot_cred": 0},
            {"id": "76543", "name": "Brown", "dept_name": "Comp. Sci.", "tot_cred": 58},
            {"id": "76653", "name": "Aoi", "dept_name": "Elec. Eng.", "tot_cred": 60},
            {
                "id": "98765",
                "name": "Bourikas",
                "dept_name": "Elec. Eng.",
                "tot_cred": 98,
            },
            {"id": "98988", "name": "Tanaka", "dept_name": "Biology", "tot_cred": 120},
        ]
    db.student.insert_many(students)
    takes = [
            {
                "id": "00128",
                "course_id": "CS-101",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "A",
            },
            {
                "id": "00128",
                "course_id": "CS-347",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "A-",
            },
            {
                "id": "12345",
                "course_id": "CS-101",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "C",
            },
            {
                "id": "12345",
                "course_id": "CS-190",
                "sec_id": "2",
                "semester": "Spring",
                "year": 2017,
                "grade": "A",
            },
            {
                "id": "12345",
                "course_id": "CS-315",
                "sec_id": "1",
                "semester": "Spring",
                "year": 2018,
                "grade": "A",
            },
            {
                "id": "12345",
                "course_id": "CS-347",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "A",
            },
            {
                "id": "19991",
                "course_id": "HIS-351",
                "sec_id": "1",
                "semester": "Spring",
                "year": 2018,
                "grade": "B",
            },
            {
                "id": "23121",
                "course_id": "FIN-201",
                "sec_id": "1",
                "semester": "Spring",
                "year": 2018,
                "grade": "C+",
            },
            {
                "id": "44553",
                "course_id": "PHY-101",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "B-",
            },
            {
                "id": "45678",
                "course_id": "CS-101",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "F",
            },
            {
                "id": "45678",
                "course_id": "CS-101",
                "sec_id": "1",
                "semester": "Spring",
                "year": 2018,
                "grade": "B+",
            },
            {
                "id": "45678",
                "course_id": "CS-319",
                "sec_id": "1",
                "semester": "Spring",
                "year": 2018,
                "grade": "B",
            },
            {
                "id": "54321",
                "course_id": "CS-101",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "A-",
            },
            {
                "id": "54321",
                "course_id": "CS-190",
                "sec_id": "2",
                "semester": "Spring",
                "year": 2017,
                "grade": "B+",
            },
            {
                "id": "55739",
                "course_id": "MU-199",
                "sec_id": "1",
                "semester": "Spring",
                "year": 2018,
                "grade": "A-",
            },
            {
                "id": "76543",
                "course_id": "CS-101",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "A",
            },
            {
                "id": "76543",
                "course_id": "CS-319",
                "sec_id": "2",
                "semester": "Spring",
                "year": 2018,
                "grade": "A",
            },
            {
                "id": "76653",
                "course_id": "EE-181",
                "sec_id": "1",
                "semester": "Spring",
                "year": 2017,
                "grade": "C",
            },
            {
                "id": "98765",
                "course_id": "CS-101",
                "sec_id": "1",
                "semester": "Fall",
                "year": 2017,
                "grade": "C-",
            },
            {
                "id": "98765",
                "course_id": "CS-315",
                "sec_id": "1",
                "semester": "Spring",
                "year": 2018,
                "grade": "B",
            },
            {
                "id": "98988",
                "course_id": "BIO-101",
                "sec_id": "1",
                "semester": "Summer",
                "year": 2017,
                "grade": "A",
            },
            {
                "id": "98988",
                "course_id": "BIO-301",
                "sec_id": "1",
                "semester": "Summer",
                "year": 2018,
                "grade": None,
            },
        ]
    db.takes.insert_many(takes)

    # Build student_enrollments: students with their enrolled courses (from takes + course)
    course_lookup = {c["course_id"]: c for c in courses}
    student_enrollments = []
    for student in students:
        student_takes = [t for t in takes if t["id"] == student["id"]]
        enrolled_courses = []
        for take in student_takes:
            course = course_lookup[take["course_id"]]
            enrolled_courses.append(
                {
                    "course_id": take["course_id"],
                    "title": course["title"],
                    "credits": course["credits"],
                    "dept_name": course["dept_name"],
                    "sec_id": take["sec_id"],
                    "semester": take["semester"],
                    "year": take["year"],
                    "grade": take["grade"],
                }
            )
        student_enrollments.append(
            {
                "id": student["id"],
                "name": student["name"],
                "dept_name": student["dept_name"],
                "tot_cred": student["tot_cred"],
                "enrolled_courses": enrolled_courses,
            }
        )
    db.student_enrollments.insert_many(student_enrollments)


if __name__ == "__main__":
    seed()
