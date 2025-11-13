from locust import HttpUser, between, task


class FileStorageUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def hit_root(self):
        self.client.get("/")

    @task
    def list_files(self):
        self.client.get("/files")

    @task
    def check_health(self):
        self.client.get("/health")

    @task
    def fetch_metrics(self):
        self.client.get("/metrics")
