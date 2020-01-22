# Psycopg connectionPool을 test with prometheus

잦은 I/O 를 DB에 수행할경우, connectionPool을 사용하여 연결을 정의한다.   
이 경우, connectionPool을 사용하지 않을 경우의 오버헤드로 인한 시간 손실을 도출 해 보기 위한 테스트 코드를 작성하였다.   
Psycopg connectionPool test [링크](https://github.com/nanaones/psycopg-test)

결과는 실제적으로 2배 이상의 차이를 나타내었으며, 200만 이상의 연결을 수행할 경우 connectionLost 가 발생한다.


