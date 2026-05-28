from locust import HttpUser, task, between


class LuxMindUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def check_system_health(self):
        self.client.get("/api/v1/admin/system-health/")

    @task(2)
    def load_homepage(self):
        self.client.get("/")