def test_root_redirects_to_static(client):
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers.get('location') == '/static/index.html'


def test_get_activities_returns_all(client):
    resp = client.get('/activities')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Known activity from seed data
    assert 'Chess Club' in data
    chess = data['Chess Club']
    assert 'description' in chess
    assert 'schedule' in chess
    assert 'max_participants' in chess
    assert 'participants' in chess


def test_signup_success(client):
    email = 'newstudent@mergington.edu'
    activity = 'Chess Club'

    # Ensure not present
    before = client.get('/activities').json()[activity]['participants']
    assert email not in before

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in client.get('/activities').json()[activity]['participants']
    assert 'Signed up' in resp.json().get('message', '')


def test_signup_duplicate_fails(client):
    activity = 'Chess Club'
    existing = client.get('/activities').json()[activity]['participants'][0]

    # First signup should return 400 when trying to sign up an existing email
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400
    assert resp.json().get('detail') == 'Student is already signed up'

    # Ensure no duplicate entries
    participants = client.get('/activities').json()[activity]['participants']
    assert participants.count(existing) == 1


def test_signup_nonexistent_activity_returns_404(client):
    resp = client.post('/activities/Nonexistent%20Club/signup?email=test@x.com')
    assert resp.status_code == 404
    assert resp.json().get('detail') == 'Activity not found'


def test_remove_participant_success(client):
    activity = 'Chess Club'
    participants = client.get('/activities').json()[activity]['participants']
    email = participants[0]

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert 'Removed' in resp.json().get('message', '')
    assert email not in client.get('/activities').json()[activity]['participants']


def test_remove_participant_not_found_returns_404(client):
    activity = 'Chess Club'
    email = 'not-present@mergington.edu'

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
    assert resp.json().get('detail') == 'Participant not found'
