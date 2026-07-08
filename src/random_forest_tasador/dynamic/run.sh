locust --headless -f locustfile.py -u 1024 --processes 24 -H http://${VM_OR_TARGET_HOST}
