docker run --network host -v $PWD/src:/mnt/locust -v $PWD/base64_images:/mnt/social_images -v $HOME/sinan_locust_log:/mnt/locust_log yz2297/locust_openwhisk \
	-f /mnt/locust/socialml_rps_1.py \
	--csv=/mnt/locust_log/social --headless -t $1 \
	--host http://${VM_OR_TARGET_HOST}:8080 --users $2 \
	--logfile /mnt/locust_log/social_locust_log.txt