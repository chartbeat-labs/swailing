Swailing
====

An opinionated logging framework.

http://www.postgresql.org/docs/9.4/static/error-style-guide.html

Uses the `token bucket algorithm`__::

  logger = swailing.Logger(name or logging.Logger)
  
  logger.info(
      'this is the primary message: %d' % 12345,
      'this is an optional detail: %s failed' % 'syscall',
      'also an optional hint to do yadda yadda',
  )

.. __: https://en.wikipedia.org/wiki/Token_bucket

That outputs to the supplied logger::

  this is the primary message: 12345
  this is an optional detail: syscall failed
  HINT: also an optional hint to do yadda yadda

Or in json format::

  {
    name: 'NAME',
    level: 'INFO',
    primary: 'this is the primary message: 12345',
    detail: 'this is an optional detail: syscall failed',
    hint: 'also an optional hint to do yadda yadda'
  }

Throttling::

  logger = swailing.Logger(name or logging.Logger, fill_rate=100, capacity=1000)
  
  # lots of calls to logger...
  # a pause...
  
  logger.info('then what happens?')

Outputs::

  (...throttled 2342 log lines...)
  then what happens?

Actually, maybe this is the official syntax::

  logger = swailing.Logger()
  
  with logger.info() as L:
      L.primary('some error %d', 1234)
      L.detail('some detail: %s failed', 'syscall')
      L.hint('you should really ...')

  # but you can always fallback to:

  logger.info('this is a regular log call %d', 12345)
