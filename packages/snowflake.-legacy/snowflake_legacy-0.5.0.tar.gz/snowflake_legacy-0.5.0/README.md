# The snowflake._legacy package

Historically, the `snowflake` package on PyPI was an unrelated package owned
by an independent developer not affiliated with
[Snowflake](https://www.snowflake.com/).  After friendly discussion in
2023, it was agreed to transfer the PyPI `snowflake` package name to
Snowflake.

In order to provide a more manageable transition, Snowflake has agreed to
maintain some backward compatibility with the old `snowflake` package, now
renamed to [snowflake-uuid](https://pypi.org/project/snowflake-uuid/).  For a
period of one year, existing users of the old package will be able to:

* `import snowflake` and call `snowflake.snowflake()` to return the contents
  of `/etc/snowflake` as a string, if it exists.  No validation of the value
  is performed.  If `/etc/snowflake` doesn't exist, a `FileNotFoundError` will
  be raised.  `snowflake.snowflake()` takes a single string argument which
  names an alternative path to read from, and this is supported in the legacy
  API.
* `snowflake.make_snowflake()` will always raise a `NotImplementedError` and
  point users to the new `snowflake-uuid` package.

It is highly recommended that all consumers of the old `snowflake` package
change their dependency to `snowflake-uuid` as soon as possible.
