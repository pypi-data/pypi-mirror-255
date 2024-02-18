# AUDIT FOR SQLAlchemy and Mongoengine

Library for auditing models made with SQLAlchemy and Mongoengine.
This library exposes a signal which you can use to add your custom method.
 
## Instalation

Use following command:
```bash
pip install audit-flask
```

## Usage
This library exposes a signal which you can use to add your custom method, this method receives kwargs where predefined arguments will arrive.


**How is it used in SQLAlchemy?**

Import library and then "Register" your model using the **keep_logs_models method**, as follows:"

```python
from audit-flask import sqlalchemy

class Model:
    ...

sqlalchemy.keep_logs_models(Model)

```
Then, conect the **"signal"** signal with your custom method

```python
def custom_method(*args, **kwargs):
    ...

sqlalchemy.signal.connect(custom_method)

```

## Kwargs in your custom method
If   `SETTINGS.HEADERS = FALSE `

| Name | Type    | Desciption|
| :---:   | :---: | :---: |
| object_pk | int   | Primary key   |
| content_type | str   | Name of the table or collection |
| object_repr | dict   | Object in dictionary after changes  |
| action | str   | It can be any of the following options ['create', 'delete', 'update']   |
| changes | str   | Object changes   |
| object_before_changed | dict   | Object in dictionary before changes    |

If   `SETTINGS.HEADERS = True `

Same as above, with two additional keys.

| Name | Type    | Desciption|
| :---:   | :---: | :---: |
| remote_addr | dict   | Corresponds to the headers of the request made |
| user | str   | Dictionary with the keys assigned in `SETTINGS.USER_VALIDATE_HEADERS`  |


## Additional configuration

- If you have a key that you need to extract for the user kwargs, add the keys in the `SETTINGS.USER_VALIDATE_HEADERS` configuration by default you have assigned: `['X-User-Id', 'X-Auth-User-Id']`.
- If you do not want to get the kwargs remote_addr and user, asgine `SETTINGS.HEADERS = False`


## Dependencies

- flask==1.1.2.  # If SETTINGS.HEADERS = True, deafult is True
- blinker==1.4
- mongoengine==0.23.1
- sqlalchemy==1.3.22

## License

[MIT](https://choosealicense.com/licenses/mit/)


## Authors

- [@jrosalesmeza](https://www.github.com/jrosalesmeza)

