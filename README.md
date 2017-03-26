Real-Time TCP
=============

This is a demonstration of how you could implement your own simple protocol over TCP.

The goal of the code is primarily educational although such implementation has been successfully used in production.

*Note:*
Using Python 3.4+.

Running example
---------------

- Install virtualenv & dependencies
```bash
$ virtualenv venv -p python3       #  create virtual environment
$ source venv/bin/activate         #  activate virtual environment
$ pip install -r requirements.txt  #  install requirements
```

- Run server
```bash
$ python real_time/server.py
```

- Run client
```bash
$ python real_time/client.py
```

<sub>Presented by [databrawl.com](https://databrawl.com)</sub>