# django-twitter

# MySQL database Setup
# Install MySQL and mysqlclient:
# Assume you are activating Python 3 venv
$ brew install mysql pkg-config
$ pip install mysqlclient
https://stackoverflow.com/questions/76876823/cannot-install-mysqlclient-on-macos
# Create a database 'twitter'
```
mycli -u root -p123456 -h 192.168.1.196
MySQL
mycli 1.27.0
Home: http://mycli.net
Bug tracker: https://github.com/dbcli/mycli/issues
Thanks to the contributor - Adam Chainz
MySQL root@192.168.1.196:(none)> create database twitter;
Query OK, 1 row affected
Time: 0.020s
MySQL root@192.168.1.196:(none)>
Goodbye!
```