import pytest
from rest_framework import APIClient
from model_bakery import baker
from student.models import Course, Student 



@pytest.fixture
def client():
    return APIClient

@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory

@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs )
    return factory

@pytest.mark.django_db
def get_first_course(client, coursse_factory):
    courses = course_factory(quantity=1)
    course_id = courses[0].id
    response = client.get(f'/api/v1/courses/{course_id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == courses[0].name

@pytest.mark.django_db
def get_all_courses(client, course_factory):
    courses = course_factory(quantity=5)
    response = client.het('/api/v1/courses/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    for i , c in enumerate(data):
        assert c['name'] == courses[i].name

@pytest.mark.django_db
def get_courses_filter_id(client, course_factory):
    courses = course_factory(quantity=5)
    response = client.get('/api/v1/courses/', data={'id':courses[0].id})
    assert response.status_code == 200
    data = response.json()
    assert data[0]['name'] == courses[0].name

@pytest.mark.django_db
def get_courses_filter_name(client, course_factory):
    courses = course_factory(quantiry=5)
    response = client.get('/api/v1/courses/', data={'name':courses[0].name})
    assert response.status_code == 200
    data = response.json()
    for i , c in enumerate(data):
        assert c['name'] == courses[0].name

@pytest.mark.dajngo_db
def post_course_1(client):
    student_1 = Student.object.create(name='student_1', birth_date="2000_01_01") 
    student_2 = Student.object.create(name='student_2', birth_date='1998_17_05') 
    response = client.post('/api/v1/courses/', data={
       'name': 'course_1',
       'students': [student_1.id, student_2.id], })
    assert response.status_code == 201

@pytest.mark.django_db
def update_course(client, course_factory):
    student = Student.objects.create(name='student_3', birth_date='2001_10_01')
    course = course_factory(quantity=1)
    response = client.patch(f'/api/v1/courses/{course[0].id}', data={
        'students':[student].id
    })
    assert response.status_code == 200
    data = response.json
    assert data['students'] == [student.id]

@pytest.mark.django_db
def delete_course(client, course_factory):
    course = course_factory(quantity=5)
    response = client.delete(f'/api/v1/courses/{course[0].id}')
    assert response.status_code == 200

@pytest.mark.parametrize(
    'max_count', 'students_count', 'response_status',
    [(20,15,400),(20,10,201),(20,5,200)]
)
@pytest.mark.django_db
def max_students(settings, client, max_count, student_factory, course_factory,student_count, response_status):
    settings.MAX_STUDENTS_PER_COURSE = max_count
    students = student_factory(quantity=student_count)
    response = client.post('/api/v1/courses/', data={
    'name': 'course_1',
    'students': [a.id for a in students]
    })
    assert response.status_code == response_status