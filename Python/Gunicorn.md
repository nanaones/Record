## Gunicorn을 미들웨어로 사용하였을때, Gevent worker는 Thread 옵션이 필요할까요?

 [이 글에 담긴 질문에 대한 해결법을 찾아보기 위한 내용입니다. ](https://medium.com/@nara03050/nginx-%ED%99%98%EA%B2%BD%EC%97%90%EC%84%9C-python3%EB%A1%9C-back-end-%EA%B5%AC%EC%B6%95%ED%95%98%EA%B8%B0-gunicorn%EA%B3%BC-gevent%EC%95%8C%EC%95%84%EB%B3%B4%EA%B8%B0-473d73aa155a)

결과적으로 의미가 없는것을 확인할 수 있었다.

이를 확인하기 위해서 thread 옵션을 변경해가며 테스트를 해보았다.  
테스트에 사용된   
[test flask Server code](Python/gunicorn/flaskServer/main.py)

---





---
#### command
```
$ gunicorn --access-logfile /log/logaccess_log --error-logfile /log/error_log -b 0.0.0.0:8000 main:app -w 2 --thread 4 -k gevent &
```

### 결과

#### $ ps -L -C gunicorn -o pid,pcpu,pmem,size,vsize 

```log

 PID  PPID %CPU %MEM  SIZE    VSZ
 6197     8  0.8  0.0     0  47892
 6200  6197  2.9  0.1     0  63228
 6201  6197  2.8  0.1     0  63272
 6475  6201  0.0  0.0     0  63528
 6486  6200  0.0  0.0     0  63748  
--- 
 PID  PPID %CPU %MEM  SIZE    VSZ
 6197     8  0.8  0.0     0  47892
 6200  6197  2.7  0.1     0  63228
 6201  6197  2.7  0.1     0  63136
 6452  6201  0.0  0.0     0  63136  
--- 
 PID  PPID %CPU %MEM  SIZE    VSZ
 6197     8  0.8  0.0     0  47892
 6200  6197  2.7  0.1     0  63092
 6201  6197  2.6  0.1     0  63136
 6455  6200  0.0  0.0     0  63228 
```

PID 6197이 main Process 로서 6200, 6201 의 ParentProcess 가 된다.  
*와중에 왜 6475, 6486 가 튀어나오는지 모르겠다.*  
할당된 CPU(%)와 메모리(%)를 보면, 제대로 워커에 할당된것을 확인할 수 있다.

---

