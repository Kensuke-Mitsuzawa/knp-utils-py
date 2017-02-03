# What's this ?

- Wrapper functions for Japanese parser [KNP](http://nlp.ist.i.kyoto-u.ac.jp/?KNP)
- This package run KNP as multi-threading job using sqlite3 as backend DB

# Contribution

- Faster processing-time than other ways to call KNP
- Json style I/O, thus you can call it as API like
- Commandline interface

At my environment(MacBook Pro Early2015)
Each way takes following time for processing 24 input-documents.

```
[knp-utils] elapsed_time:14.52339506149292 [Sec]
[Native KNP subprocess] elapsed_time:23.880084991455078 [Sec]
[Native KNP server] elapsed_time:22.08908200263977 [Sec]
[Pyknp] elapsed_time:36.08908200263977 [Sec]
```

# Requirement

- Juman
- KNP
- Sqlite3
- Python
    - 2.x (checked under 2.7)
    - 3.x (checked under 3.5)

# Setup

## Juman

```
% wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2&name=juman-7.01.tar.bz2" -O juman-7.01.tar.bz2
% tar jxf juman-7.01.tar.bz2
% cd juman-7.01
% ./configure && make  && make install
```

## KNP

```
% wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.16.tar.bz2&name=knp-4.16.tar.bz2" -O knp-4.16.tar.bz2
% tar jxf knp-4.16.tar.bz2
% cd /knp-4.16
% ./configure && make  && make install
```

## package

```
python setup.py install
```

# Sample

## From python code

See `example.py`

## From CL

```
python knp_utils.py -i ./tests/resources/input_sample.json
```

