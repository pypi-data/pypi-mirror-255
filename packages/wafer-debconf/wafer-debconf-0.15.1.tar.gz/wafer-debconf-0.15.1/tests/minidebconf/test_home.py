class TestHome:
    def test_visitor(self, client):
        client.logout()
        res = client.get("/")
        assert res.status_code == 200

    def test_logged_in(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_superuser(self, user, client):
        user.is_staff = user.is_superuser = True
        user.save()
        res = client.get("/")
        assert res.status_code == 200
