import pytest
from django.urls import reverse

from students.models import Course


# @pytest.mark.django_db
# def test_fixtures_work(client, course_factory):
#     course = course_factory()
#     print(course.id, course.name)
#     assert course.id is not None

@pytest.mark.django_db
def test_get_course(client, course_factory):
    course = course_factory(name="Тест")

    url = reverse('courses-detail', args=[course.id])
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data['name'] == course.name


@pytest.mark.django_db
def test_get_courses_list(client, course_factory):
    courses = course_factory(_quantity=3)

    url = reverse('courses-list')
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    for i, b in enumerate(data):
        assert b['name'] ==courses[i].name


@pytest.mark.django_db
def test_filter_courses_by_id(client, course_factory):
    courses = course_factory(_quantity=3)
    target = courses[1]

    url = reverse('courses-list')
    response = client.get(url, data={'id': target.id})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == target.id


@pytest.mark.django_db
def test_filter_courses_by_name(client, course_factory):
    courses = course_factory(_quantity=3)
    target = courses[1]

    url = reverse('courses-list')
    response = client.get(url, data={'name': target.name})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == target.name


@pytest.mark.django_db
def test_create_course(client):
    url = reverse('courses-list')
    payload = {'name': 'python-разработчик'}

    response = client.post(url, data=payload, format='json')

    assert response.status_code == 201
    assert response.json()['name'] == payload['name']
    assert Course.objects.count() == 1


@pytest.mark.django_db
def test_update_course(client, course_factory):
    course = course_factory(name='python-разработчик')

    url = reverse('courses-detail', args=[course.id])
    response = client.patch(url, data={'name': 'java-разработчик'}, format='json')

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.name == 'java-разработчик'


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    course = course_factory()

    url = reverse('courses-detail', args=[course.id])
    response = client.delete(url)

    assert response.status_code == 204
    assert not Course.objects.filter(id=course.id).exists()


@pytest.mark.parametrize(
    'students_count, expected_status',
    [
        (1, 201),
        (2, 201),
        (3, 400),
    ]
)
@pytest.mark.django_db
def test_students_limit(client, student_factory, settings, students_count, expected_status):
    settings.MAX_STUDENTS_PER_COURSE = 2
    students = student_factory(_quantity=students_count)

    response = client.post(
        reverse('courses-list'),
        data={'name': 'Тест', 'students': [a.id for a in students]},
        format='json'
    )

    assert response.status_code == expected_status