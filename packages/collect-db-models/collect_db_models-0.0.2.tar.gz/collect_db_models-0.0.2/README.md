# collect db models

collect sqlalchemy models to one file

## 安装

```sh
pip install collect-db-models
```

## 使用

```sh
flask collect-db-models > your_project/models/__init__.py2
```

如果没有报错，就可以把文件更名为\_\_init\_\_.py


## Flask项目需要符合下面的结构

```plain
your_project/
│
├──core/
│   └── __init__.py
├──models/
│   └── __init__.py
```

your_project/core/\_\_init\_\_.py

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```
