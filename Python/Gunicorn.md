# Gunicorn을 미들웨어로 사용하였을때, Gevent worker는 Thread 옵션이 필요할까요?

 [오래전에 써 놓은 글에 질문이 달렸다.](https://medium.com/@nara03050/nginx-%ED%99%98%EA%B2%BD%EC%97%90%EC%84%9C-python3%EB%A1%9C-back-end-%EA%B5%AC%EC%B6%95%ED%95%98%EA%B8%B0-gunicorn%EA%B3%BC-gevent%EC%95%8C%EC%95%84%EB%B3%B4%EA%B8%B0-473d73aa155a)  
질문의 내용에 대해서 알아보다가, Gunicorn GitHub Issue 에서 다음과 같은 내용을 확인하였다.

https://github.com/benoitc/gunicorn/issues/1045#issuecomment-275678536

`--thread` 옵션은 동기(Sync) 타입의 worker를 위한 옵션이라는 설명이다.
따라서, 비동기(Async) 타입의 Worker인 Gevent Worker는 Thread 옵션의 영향을 받지 않는다.  

---


[GeventletWorker code](https://github.com/benoitc/gunicorn/blob/9c1438f013/gunicorn/workers/geventlet.py) 를 보면, Greenlet hread pool에서 gthread를 사용한다.
- 각 worker는 각각 사용하는 기술이 다르며, 이는 worker의 성질에 따라 결정된다. 

Gevent와 같은 비동기 worker들은 AsyncWorker를 상속받으며, 
[AsyncWorker](https://github.com/benoitc/gunicorn/blob/9c1438f013/gunicorn/workers/base_async.py)는 RequestHandler가 multithread 컨텍스트에 True 로 기록하여 전달한다.

- 사실 비동기인거지, multithread로 구성되어있지 않은 Worker인데 설정상 multithread로 구분 되어있어서 혼동이 있었다.


```python
    def handle_request(self, listener_name, req, sock, addr):
        request_start = datetime.now()
        environ = {}
        resp = None
        try:
            self.cfg.pre_request(self, req)
            resp, environ = wsgi.create(req, sock, addr,
                                        listener_name, self.cfg)
            environ["wsgi.multithread"] = True
            self.nr += 1
            if self.alive and self.nr >= self.max_requests:
```


---

# Gunicorn 의 worker 옵션은 사용자가 최적화 하기 나름입니다.

위 내용을 확인하며 GitHub Issue를 둘러 보다가 다음과같은 이슈를 확인하였다.   
https://github.com/benoitc/gunicorn/issues/1045#issuecomment-269575459

결국, 사용자가 thread를 사용할지, worker를 사용할지는 GIL에서 오는 오버헤드와 프로세스의 메모리 오버헤드중에서 선택하는 것이며 
(동기, 비동기 Worker를 사용하였을때를 말 하는 것 으로 보인다.  
동기Worker의 경우에는 thread옵션을 통해서 thread의 수를 결정하게 되는데, 파이썬에서는 GIL에 의해서 I/O 작업이 아닌 CPU 연산을 수행하는 작업은 GIL에 의해, lock이 실행되어, 동기와 마찬가지의 속도로 작업이 수행된다.  
 worker를 사용하여 별도의 프로세스를 동작시키는 경우, GIL의 Lock()은 없어지지만, 메모리 오버헤드가 상당히 커지는 단점을 지니게 된다.) 결과적으로는 tradeoff 이기 때문에 어떤 worker를 사용할지, 몇 개의 worker를 사용할지 테스트 기반으로 결정해야한다는 내용 이었다.

이를 확인하기 위해서 thread 옵션을 변경해가며 테스트를 해보았다.  
테스트에 사용된 [test flask Server code](https://github.com/nanaones/Record/blob/master/Python/gunicorn/flaskServer/main.py)

---

1. `--thread` 옵션 테스트  

    * [2 Worker 2 Thread](https://github.com/nanaones/Record/blob/master/Python/gunicorn/flaskServer/results/changeThreadOption/result2worker2thread.txt)  

            Requests per second:    60.79 [#/sec] (mean)

    * [2 Worker Only](https://github.com/nanaones/Record/blob/master/Python/gunicorn/flaskServer/results/changeThreadOption/result2workeronly.txt) 

            Requests per second:    64.84 [#/sec] (mean)


    * [4 Worker 2Thread](https://github.com/nanaones/Record/blob/master/Python/gunicorn/flaskServer/results/changeThreadOption/result4worker2thread.txt)  
    
            Requests per second:    38.92 [#/sec] (mean)

2. `--worker-connections` 옵션 테스트  
    * Default start command is  

    ` $ gunicorn --access-logfile /log/logaccess_log --error-logfile /log/error_log -b 0.0.0.0:8000 main:app -w 2 --worker-connections [INT] -k gevent`  

    * [`--worker-connections 100`](https://github.com/nanaones/Record/blob/master/Python/gunicorn/flaskServer/results/changeWorkerConnections/result2workerworkerconnections10.txt)

            Requests per second:    94.01 [#/sec] (mean)


    * [`--worker-connections 10`](https://github.com/nanaones/Record/blob/master/Python/gunicorn/flaskServer/results/changeWorkerConnections/result2workerworkerconnections100.txt)

            Requests per second:    120.42 [#/sec] (mean)

---
#### result
1. `--thread` 옵션
- [gunicorn gthread Worker Code를 확인해 보면](https://github.com/benoitc/gunicorn/blob/9c1438f013/gunicorn/workers/gthread.py#L88), 처음 프로세스를 만들때, config 내의 threads 숫자대로 thread를 만드는걸 확인할 수 있다.

- 하지만 [gunicorn Gevent Worker Code를 확인해 보면](https://github.com/benoitc/gunicorn/blob/9c1438f013/gunicorn/workers/ggevent.py), gthread Worker와 같은 threadPool 부분이 없다.  

- thread 옵션 테스트의 결과와 코드를 통해 이해했지만, `--thread` 옵션은 성능에 영향을 끼치진 않는 것 으로 보인다.

2. `--workerconnections` 옵션

- [Gevent Worker Class Code](https://github.com/benoitc/gunicorn/blob/9c1438f013/gunicorn/workers/ggevent.py#L75)를 확인해 보면, gthread와는 달리 Pool에 `self.worker_connections`를 파라미터로 입력하는 것을 확인할 수 있다. 이는 gevent에서 greenlet이라는 microThread를 가지고오는 수를 지정하는 것 이며, 하나의 코루틴에서 수행될 양을 설정하는 부분이다.

3. workerconnections 옵션또한 적정값을 찾는것이 성능 최적화의 방법이다.

4. `--max-requests` 옵션
- '왜 위의 4Worker 2thread 를 사용하였을때, RequstsPerSeconds가 2Worker 보다 낮았는가'

        이 옵션은 지정된 수의 request가 worker에게 할당되어 처리가 완료되면 해당 Worker를 재시작 시키는 옵션이다.

- '왜 재시작 하지 않으면 안되는가'  
[이 부분은 지인찬스를 통해서 힌트를 얻을 수 있었다.](https://www.facebook.com/permalink.php?story_fbid=1015849825462536&id=100011125846399)     

        gevent Worker를 쓸 경우, 요청이 끊기지 않은 경우, 해당 연결에 대한 메모리를 계속 들고있다.  
        이는 프로세스 입장에서 부담이며, 결국 GC의 개념으로 재시작을 통한 리프레시를 해 주어야 한다.



#### conclusion

명확하고 신속하게 성능 최적화를 어떻게 해야 할 지 난감하다.  
생각보다 성능에 영향을 끼치는 변수가 많으며, 이를 사용자가 직접 커스터마이징 해야한다.( 물론 찾아보면 누군가 만들었을 것 같다. )



---

#### Questions

#### command
```
$ gunicorn --access-logfile /log/logaccess_log --error-logfile /log/error_log -b 0.0.0.0:8000 main:app -w 2 --thread 4 -k gevent &
```

### result

#### $ ps -L -C gunicorn -o pid,ppid,pcpu,pmem,size,vsize 

[logFile](https://github.com/nanaones/Record/blob/master/Python/gunicorn/flaskServer/results/log/2020-01-03.log)
```log
~
---
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

~
```

PID 6197이 main Process 로서 6200, 6201 의 ParentProcess 가 된다.  
*와중에 왜 6475, 6486 가 튀어나오는지 모르겠다.*  
할당된 CPU(%)와 메모리(%)를 보면, 제대로 워커에 할당된것을 확인할 수 있다.

---

