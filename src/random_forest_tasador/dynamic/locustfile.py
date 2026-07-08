from locust import FastHttpUser, TaskSet, task, between, LoadTestShape
from pathlib import Path

class WebsiteTasks(TaskSet):
    @task
    def get_index(self):
        # Test retrieving index.html
#        self.client.get("/index.lighttpd.html")
        response = self.client.get("http://${VM_OR_TARGET_HOST}/index.lighttpd.html")
        if response.status_code != 200:
            print(f"Failed request with status code: {response.status_code}")
        
class WebsiteUser(FastHttpUser):
    tasks = [WebsiteTasks]
    wait_time = between(0, 0.05)  # Simulates a wait time between 1 and 3 seconds between requests


RPS = list(map(int, Path("${EXPERIMENT_ROOT}").read_text().splitlines()))


class CustomShape(LoadTestShape):
    time_limit = len(RPS)
    spawn_rate = 100

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.time_limit:
            user_count = RPS[int(run_time)]

        # Debugging output
            print(f"Runtime: {run_time}, User Count: {user_count}, Spawn Rate: {self.spawn_rate}")
            
            return (user_count, self.spawn_rate)
        return None
