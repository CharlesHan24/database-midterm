https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

curl http://localhost:5000/member --header "Content-Type: application/json" --request POST --data '{"stuid": "1800013095", "name": "Bob", "password": "123456", "position": "sec_head", "section": 3, "contact": "123456"}' -b a.txt  -v

curl http://localhost:5000/members --header "Content-Type: application/json" --request GET --data '{"section": 0, "name": "None", "page": "1"}'

curl http://localhost:5000/member/1234567890 --header "Content-Type: application/json" --request POST --data '{"stuid": "1800013095", "name": "Bob", "password": "123456", "position": "sec_head", "section": 3, "contact": "123456"}' -b a.txt -v

curl http://localhost:80/candidate --header "Content-Type: application/json" --request POST --data '{"stuid": "1700010001", "name": "Bob", "grade": 3, "brief": "ababa", "application": [1, 3], "contact": "123456", "attachment": "hash_val"}' -b a.txt -v

curl http://localhost:80/candidate/1700010001/review --header "Content-Type: application/json" --request POST --data '{"score": 80, "text": "ababa"}' -b a.txt -v

curl http://localhost:80/candidates --header "Content-Type: application/json" --request GET  -b a.txt -v