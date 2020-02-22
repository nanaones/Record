

# FlaskSQLAlchemy

flask 기반의 API Server 를 개발하다가 했던 실수2  

[main.py](https://github.com/nanaones/case/blob/master/main.py)  


* python 의 순환참조  
FlaskSQLAlchemy 와 같은 ORM을 사용할 때 에는 순환참조를 조심해야한다. 

ORM을 난생 처음 접해본 나는 이떄문에 큰 멘탈 & 시간 타격을 받았었는데, 발생하는 원리는 다음과 같다.


1. Flask main.py 코드에서 db 객체 선언     
in [main.py](https://github.com/nanaones/case/blob/master/main.py) 

    ```python

    import json
    import os

    from flask import Flask, request, abort, Response
    from flask_cors import CORS, cross_origin
    from flask_sqlalchemy import SQLAlchemy


    if not os.getenv("DATABASEURI") is None:
        _dbms_uri = os.getenv("DATABASEURI")
    else:
        _dbms_uri = "postgresql://postgres:8015@localhost:5432/postgres?sslmode=disable"

    app = Flask(__name__)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config["SQLALCHEMY_DATABASE_URI"] = _dbms_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
    db.init_app(app)
    CORS(app)

    ...
    ```

    이부분
    ```python
    db = SQLAlchemy(app)
    db.init_app(app)
    ```

2. models.py 코드에서 main에 있는 db 객체 사용
    in [models.py](https://github.com/nanaones/case/blob/master/models.py) 

    ```python

    from main import db

    class CompanyName(db.Model):
        __tablename__ = 'WANT_COMP_NAME_TB'
        comp_name_id = db.Column('COMP_NAME_ID', db.Integer, primary_key=True)
        comp_name_nm = db.Column("COMP_NAME_NM", db.String(80))
        
        def __init__(self, comp_name_id, comp_name_nm):
            self.comp_name_id = comp_name_id
            self.comp_name_nm = comp_name_nm
    ...

    ```
    
    이부분  

    ```python
      from main import db
     ...

    ```


3. main.py 에서 models.py 에서 구현한 구현체들을 import 
    ```python
    import models
    ```

4. 순환참조 에러 발생


---

## 해결법  

아래와같이, 사용하는 부분에서 import 하면 된다.
Java에서는 이 부분을 해결해주는 라이브러리가 따로 있다고 들었는데, python도 방법이 있을 것 같다. 


```python
@app.route("/company/<int:_id>", methods=["GET"])
@cross_origin()
def company_get_by_id(_id: int):
    """
    GET HTTP METHOD
    URI 에 해당하는 회사의 종류 리턴

    :params:id      회사의 id
    """

    try:
        import models
        _data = models.Query.get_comp_data_by_comp_id(comp_name_id=_id)
        # return json.dumps(_data, ensure_ascii=False)
        return json.dumps(_data)
    except AttributeError:
        abort(400)

```

---

flask 기반의 API Server 를 개발하다가 했던 실수3

* FlaskSQLAlchemy를 ORM답게 짭시다.
    [models.py](https://github.com/nanaones/case/blob/master/models.py)  

FlaskSQLAlchemy 를 처음 만났고 ORM은 난생 처음이라 그냥 막 짰더니 아래와 같이 끔찍한 복잡도의 코드가 나왔다. 

### O(n^2)    

```python

    @staticmethod
    def get_comp_data_by_comp_id(comp_name_id: int):
        """
        입력받은 comp_name_id 를 기준으로 comp_name 반환
        """
        _tags = []
        _comp_name = CompanyName.query.filter_by(comp_name_id=comp_name_id).first().comp_name_nm
        _comp_cat_id = Query.search_comp_cat_id_by_comp_name(_company_name=_comp_name).comp_cat_id
        _tag_cat_id = Query.search_tag_cat_name_by_comp_cat_id(comp_cat_id=_comp_cat_id)
        
        for _ in _tag_cat_id:
            tag_name_id_list = Query.search_tag_id_by_tag_cat_id(_.tag_cat_id)
            for _id in tag_name_id_list:
                _tags.append(TagName.query.filter_by(tag_name_id=_id.tag_name_id).first().tag_name_nm)

        _ret = {
            "companyName": _comp_name,
            "tags": _tags
        }
        return _ret

```

아래와 같이 쿼리를 통해 잘 가져와야한다.

```python
    @staticmethod
    def get_all_tag_name():
        """
        입력되어있는 태그의 이름을 리턴한다.
        """
        _ret = {
            "tag": []
        }

        for _ in TagName.query.join(TagNameCat, TagName.tag_name_id == TagNameCat.tag_name_id).all():
            _ret["tag"].append(_.tag_name_nm)

        return _ret
```
 
