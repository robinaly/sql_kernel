A SQL Kernel for [Jupyter](http://jupyter.org/)

This package allows users to execute sql commands; one command per cell. 

The package is heavily inspired by the greate packages [ipython-sql](https://github.com/catherinedevlin/ipython-sql) and [bash_kernel](https://github.com/takluyver/bash_kernel) (some code was also taken from there).

# Example Use

The first line has to be an [SQLAlchemy connect string ](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html#database-urls). For example, to connect to ab in-memory sqlite database, the first line should be:

```sql
In [1]: sqlite://
Out[1]: Connected
```

Afterwards, you can use standard SQL commands to fill the database with values and retrieve them.

```sql
In [2]: CREATE TABLE X (firstname VARCHAR(20), lastname VARCHAR(20))
In [3]: INSERT INTO X VALUES ("John", "Smith")
In [4]: INSERT INTO X VALUES ("John", "Doe")
In [5]: SELECT * FROM X
Out[5]: 
+-----------+----------+
| firstname | lastname |
+-----------+----------+
|    John   |  Smith   |
|    John   |   Doe    |
+-----------+----------+
```
