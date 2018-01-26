# ICX Score prototype
ICX Coin을 처리하기 위한 SCORE code 예제

*주의:이것은 실제 ICX coin용 code가 아닌 SCORE 교육용 prototype입니다.*

*WARN: THIS IS NOT REAL ICX COIN SCORE code, but SCORE prototype for education.*

# Feature
* ICX 이체
* ICX 잔고 조회


## ```invoke``` Functions
블록체인에 저장되어 있는 거래 처리.

### ```POST icx_sendTransaction```
ICX 코인을 송신자 주소에서 수신자 주소로 이체한다.

- Request
   * ```jsonrpc```: "2.0"
   * ```id```: Request들의 ID. 해당 Request들의 구분용. Client가 임의로 주게 되어 있다.
   * ```method```: Function name
   * ```params```: Function parameter (JSON)
      - ```from```: 돈을 꺼낼 주소 (16진수 40자리)
      - ```to```: 돈을 보낼 주소 (16진수 40자리)
      - ```value```: 처리할 액수 (16진수, 10^18이 최대)

   Example:
```JSON
{
   "jsonrpc": "2.0",
   "id": 1,
   "method": "icx_sendTransaction",
   "params": {
	    "from": "0xb60e8dd61c5d32be8058bb8eb970870f07233155",
	    "to": "0xd46e8dd67c5d32be8058bb8eb970870f07244567",
	    "value": "0x9184e72a", 
	}
}
```
- Response
   * ```response_code```: 정상적이면 0, 아니면 다른 값을 가지고 있다. [참고자료](http://www.simple-is-better.org/json-rpc/jsonrpc20.html#examples)
   * ```tx_hash ```: Hash 값. 해당 Hash로 Transaction을 조회하면 결과 값을 알 수 있다.
   * ```more_info```: 추가 정보

   Example:
``` JSON
{
   "response_code": "0",
   "tx_hash": "be31ef079c03e308a4bddf8412a0ebe7f545cbfa82c3d8c2c6c5b3c40756583a",
   "more_info": ""
}
```


## ```query``` Functions
Smart Contract 질의 목록

### ```GET icx_getBalance```
ICX 주소의 잔고 금액을 조회한다.

- Request
   * ```jsonrpc```: "2.0"
   * ```id```: Request ID
   * ```method```: "icx_getBalance"
   * ```params```: 계좌주소 (16진수 40자리)

Example :
```JSON
{
    "jsonrpc": "2.0",
    "id": 123,
    "method": "icx_getBalance",
    "params": "0x0011223344556677889900112233445566778899"
}

```

- Response
   * ```jsonrpc```: "2.0"
   * ```id```: Request ID
   * ```result```: 액수 (16진수)

Example:
```JSON
{
    "jsonrpc": "2.0",
    "id": 123,
    "result": "0x1"
}
```
