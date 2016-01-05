Swailing
====

An opinionated logging framework.

http://www.postgresql.org/docs/9.4/static/error-style-guide.html

Uses the `token bucket algorithm`__::

  logger = swailing.Logger(name or logging.Logger)
  
  with logger.info() as L:
      L.primary('this is the primary message: %d', 12345)
      L.detail('this is an optional detail: %s failed', 'syscall')
      L.hint('also an optional hint to do yadda yadda')

.. __: https://en.wikipedia.org/wiki/Token_bucket

That outputs to the supplied logger::

  this is the primary message: 12345
  this is an optional detail: syscall failed
  also an optional hint to do yadda yadda

Or in json format::

  {
    level: 'INFO',
    primary: 'this is the primary message: 12345',
    detail: 'this is an optional detail: syscall failed',
    hint: 'also an optional hint to do yadda yadda'
  }

But you can always fallback to::

  logger.info('this is a regular log call %d', 12345)

Throttling::

  logger = swailing.Logger(logging.getLogger(), fill_rate=100, capacity=1000)
  
  # A burst of 1000+ calls, exceeding 100 / second...
  # Then a pause of at least 1/100 second...
  
  logger.info('then what happens?')

Outputs the first 1000 calls, and then::

  (...throttled 2342 log lines...)
  then what happens?
