# update-query

This is a command line tool to support "[データベーススキーマ変更の失敗しにくい管理方法](http://qiita.com/items/fd996de8c5d58d95047d)".

## Requirements

* Python 2.7

## How to Install

Just `git clone` or download `update-query.py` via browser and `chmod +x update-query.py`.

## How to use

Basically, execute like `$ ./update-query.py` or `$ python update-query.py`.

This is the overview of `update-query.py`

```
$ ./update-query.py  --help
usage: update-query.py [-h] command ...

Update query management tool

optional arguments:
  -h, --help  show this help message and exit

commands:
  command
    init      initialize with new token
    create    create new update query
    apply     concatenate update queries together and create a patch
    tokens    list up all tokens
```

Also, you can get more helps for each command with `-h` option like `$ ./update-query create -h`

### Create new token

```
# run in interactive mode
$ ./update-query.py init 

# or non-interactive mode
$ ./update-query.py init [environment name]

```

### Create new update query file


```
# run in interactive mode
$ ./update-query.py create

# or non-interactive mode
$ ./update-query.py create [file name]
```

For example,

```
$ ./update-query.py create
New file name: add zipcode to user      <= You can use space here, and space will be underscore!
New file '20120718_1929_add_zipcode_to_user.sql' was created.
Please edit it.
```

### Organize update query files to one file

```
# run in interactive mode
$ ./update-query.py apply

# or non-interactive mode
$ ./update-query.py apply [environment name]
```

For eample,

```
$ ./update-query.py apply
We know these environments:
  * develop
  * staging
Environment name: develop
Token renamed 20120718_1926~develop.apply_token -> 20120718_1932~develop.apply_token
------------------------------
Patch file was created!

  * patch.develop.20120718_1932.sql

Please apply the patch update queries in above file to the SQL server.
After you apply, please delete patch file from here.
```

```
$ ls -la
drwxr-xr-x  10 suin  staff   340B  7 18 19:33 ./
drwxr-xr-x  31 suin  staff   1.0K  7 18 19:17 ../
-rw-r--r--   1 suin  staff    28B  7 18 19:27 20120718_1927~staging.apply_token
-rw-r--r--   1 suin  staff     0B  7 18 19:29 20120718_1929_add_zipcode_to_user.sql
-rw-r--r--   1 suin  staff     0B  7 18 19:31 20120718_1931_add_address_to_user.sql
-rw-r--r--   1 suin  staff     0B  7 18 19:32 20120718_1932_create_view_user_bills.sql
-rw-r--r--   1 suin  staff    28B  7 18 19:26 20120718_1932~develop.apply_token
-rw-r--r--   1 suin  staff   130B  7 18 19:32 patch.develop.20120718_1932.sql
```


### List all tokens

```
$ ./update-query.py tokens
```


## License

MIT License

