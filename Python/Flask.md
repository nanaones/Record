

# Flask

[flask 기반의 API Server 를 개발하다가 했던 실수](https://github.com/nanaones/case/blob/master/main.py)  

* 만들어진 API가 다국어가 포함된 json Return 작업을 수행할때 json 라이브러리의 dumps 를 사용한다면 `ensure_ascii=False`

리턴에는 다음과 같이 반드시 `ensure_ascii=False` 옵션을 `json.dumps`에 추가해줄것, 

```python
    try:
        import models
        tag_name = request.args.get("tagName").strip()
        _data = models.Query.get_company_name_by_tag_name(tag_name)
        return json.dumps(_data, ensure_ascii=False)
    except AttributeError:
        abort(400)
```

아래와 같이 와야하는 데이터가
```json
{
    "companyName": "원티드랩", 
    "tags": [ "tag_20", "태그_20", "タグ_20", "tag_16", "태그_16", "タグ_16"]
    }
```
브라우저에서는 아래와 같이 깨져서 오게 된다.


```json
{
    "companyName": "\uc6d0\ud2f0\ub4dc\ub7a9", 
    "tags": ["tag_20", "\ud0dc\uadf8_20", "\u30bf\u30b0_20", "tag_16", "\ud0dc\uadf8_16", "\u30bf\u30b0_16"]
}
```
