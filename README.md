### There is mini-server with HEAD & GET methods  

#### Files
**httpd.py** - entry point  
*Server code - read events, receive packages and sending answer*


**logic.py**  
*get request and return response & code for it*

**IT's working on server now, can use on**   http://109.94.208.27/httptest/wikipedia_russia.html


#### TESTS
httptest.py  
directory index file exists ... ok  
document root escaping forbidden ... ok  
Send bad http headers ... ok  
file located in nested folders ... ok  
absent file returns 404 ... ok  
urlencoded filename ... ok  
file with two dots in name ... ok  
query string after filename ... ok  
filename with spaces ... ok  
Content-Type for .css ... ok  
Content-Type for .gif ... ok  
Content-Type for .html ... ok  
Content-Type for .jpeg ... ok  
Content-Type for .jpg ... ok  
Content-Type for .js ... ok  
Content-Type for .png ... ok  
Content-Type for .swf ... ok  
head method support ... ok  
directory index file absent ... ok  
large file downloaded correctly ... ok  
post method forbidden ... ok  
Server header exists ... ok  
----------------------------------------------------------------------
Ran 22 tests in 0.292s  

OK


#### ab -n 50000 -c 100 -r http://localhost:8080/
This is ApacheBench, Version 2.3 <$Revision: 1430300 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)  
Completed 5000 requests  
Completed 10000 requests  
Completed 15000 requests  
Completed 20000 requests  
Completed 25000 requests  
Completed 30000 requests  
Completed 35000 requests  
Completed 40000 requests  
Completed 45000 requests  
Completed 50000 requests  
Finished 50000 requests  


Server Software:  
Server Hostname:        localhost  
Server Port:            8080  

Document Path:          /  
Document Length:        0 bytes  

Concurrency Level:      100  
Time taken for tests:   1.586 seconds  
Complete requests:      50000  
Failed requests:        75001  
   (Connect: 0, Receive: 50001, Length: 0, Exceptions: 25000)  
Write errors:           0  
Total transferred:      0 bytes  
HTML transferred:       0 bytes  
Requests per second:    31528.14 [#/sec] (mean)  
Time per request:       3.172 [ms] (mean)  
Time per request:       0.032 [ms] (mean, across all concurrent requests)  
Transfer rate:          0.00 [Kbytes/sec] received  
  
Connection Times (ms)  
              min  mean[+/-sd] median   max  
Connect:        0    0   0.0      0       0  
Processing:     0    0   0.1      0      11  
Waiting:        0    0   0.0      0       0  
Total:          0    0   0.1      0      11  

Percentage of the requests served within a certain time (ms)  
  50%      0  
  66%      0  
  75%      0  
  80%      0  
  90%      0  
  95%      0  
  98%      0  
  99%      0  
 100%     11 (longest request)  
 
 
#### wrk -t8 -c200 -d30s --timeout 2s http://localhost:80
Running 30s test @ http://localhost:80
  8 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    30.67ms  122.48ms   1.67s    96.81%
    Req/Sec   123.69    147.89   831.00     86.09%
  17731 requests in 30.08s, 2.47MB read
  Socket errors: connect 0, read 17960, write 0, timeout 5
  Non-2xx or 3xx responses: 17731
Requests/sec:    589.53
Transfer/sec:     84.05KB