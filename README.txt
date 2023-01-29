==Тестирование пропускной способности==
ip route - получить ip 
wrk -t8  -d30s http://ip:8000/users/1/products


