### Parse HTML into structured text.

## On Linux:

$ virtualenv -p python3.6 .
$ source bin/activate 
$ pip install -r requirements.txt

 # TODO: Add info about env on Windows
  
 ```
$ ./grab_article.py -h
usage: grab_article.py [-h] [-v] url

Parse HTML into structured text.

positional arguments:
  url            URL to grab html from.

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Verbose output
```

### Examples 

```
./grab_article.py https://lenta.ru/news/2017/05/25/ka62/ -v

Page https://lenta.ru/news/2017/05/25/ka62/ was downloaded successful.

Вертолет  .....
....

File was successfully stored as lenta.ru/news/2017/05/25/ka62/ka62.txt

```

```
./grab_article.py https://www.gazeta.ru/culture/2017/05/25/a_10693097.shtml

Here is nothing in output


File was stored into www.gazeta.ru/culture/2017/05/25/a_10693097.txt

```