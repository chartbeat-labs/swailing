Swailing
====

An opinionated logging library for applications that produce a
debilitating amount of log output.

Swailing uses the
[token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket)
and provides facilities for
[PostgreSQL style error logs](http://www.postgresql.org/docs/9.4/static/error-style-guide.html).


Token Bucket
----

The token bucket algorithm is a simple mechanism for throttling
burstable events. There are two parameters: fill rate and
capacity. The fill rate is the number of tokens that a bucket
accumulates per second. The capacity is the largest number of tokens
that the bucket holds. Each time your application emits log output,
Swailing consumes one of the tokens in the bucket. Thus, we allow
outputting a steady rate of messages less than or equal to the fill
rate, with the capability of bursting up to the capacity.


PostgreSQL Style Error Logs
----

In addition to plain log lines (called primary), Swailing allows the
program to output detail and hint lines as well. See the
[PostgreSQL guide](http://www.postgresql.org/docs/9.4/static/error-style-guide.html)
for what the semantic differences are.


Usage
----

```python
logger = swailing.Logger(logging.getLogger())

with logger.info() as L:
    L.primary('this is the primary message: %d', 12345)
    L.detail('this is an optional detail: %s failed', 'syscall')
    L.hint('also an optional hint to do yadda yadda')
```

That outputs to the supplied logger:

```
this is the primary message: 12345
this is an optional detail: syscall failed
also an optional hint to do yadda yadda
```

But you can always fallback to regular style logging:

```python
logger.info('this is a regular log call %d', 12345)
```

You can silence details and hints at runtime by setting the verbosity:

```python
logger.set_verbosity(swailing.PRIMARY)

with logger.info() as L:
    L.primary('this is the primary message: %d', 12345)
    L.detail('this is an optional detail: %s failed', 'syscall')
    L.hint('also an optional hint to do yadda yadda')
```

Outputs:

```
this is the primary message: 12345
```

Throttling:

```python
logger = swailing.Logger(logging.getLogger(), fill_rate=100, capacity=1000)

# A burst of 1000+ calls, exceeding 100 / second...
# Then a pause of at least 1/100 second...

logger.info('then what happens?')
```

Outputs the first 1000 calls, and then:

```
(...throttled 2342 log lines...)

then what happens?
```
