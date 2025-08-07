from locust import HttpUser, task, between


class LibraryUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    def on_start(self):
        """Called when a Locust user starts, used for logging in."""
        response = self.client.post(
            "/api/users/login/",
            json={
                "email": "member1@example.com",  # Assumes this user exists
                "password": "password123",
            },
        )
        self.token = response.json()["access"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def search_books(self):
        """Simulates a user searching for books (high-read endpoint)."""
        self.client.get(
            "/api/books/?search=django",
            headers=self.headers,
            name="/api/books/?search=[query]",
        )

    @task
    def list_books(self):
        """Simulates a user browsing the book list."""
        self.client.get("/api/books/", headers=self.headers)

    @task
    def view_own_profile(self):
        """Simulates a user viewing their own profile."""
        self.client.get("/api/users/profile/", headers=self.headers)
