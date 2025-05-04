def test_feedback_post(client):
    response = client.post('/feedback', data={'feedback_text': 'Thank for your serve!'}, follow_redirects=True)
    assert b"Feedback received" in response.data

def test_feedback_empty(client):
    response = client.post('/feedback', data={'feedback_text': ''}, follow_redirects=True)
    assert response.status_code == 200
