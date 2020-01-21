# Psycopg connectionPool을 test with prometheus

잦은 I/O 를 DB에 수행할경우, connectionPool을 사용하여 연결을 정의한다. 
이 경우, connectionPool을 사용하지 않을 경우의 오버헤드로 인한 시간 손실을 도출 해 보기 위한 테스트 코드를 작성하였다.   
Psycopg connectionPool test [링크](https://github.com/nanaones/psycopg-test)




