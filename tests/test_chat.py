def test_chat_valid_input(client):
    response = client.post('/chat', data={'user_input': 'Hello!'})
    assert response.status_code == 200
    assert b'User' in response.data
    assert b'AI' in response.data

