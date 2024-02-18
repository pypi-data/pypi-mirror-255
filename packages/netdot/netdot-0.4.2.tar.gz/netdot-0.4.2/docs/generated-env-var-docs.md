

# Netdot Python API Environment Variables
<a id="netdot-python-api-environment-variables"></a>

> Generated using `netdot.config.help()`
>
> Version 0.4.2 documentation generated on Feb 07, 2024 at 08:11AM 

```

  --terse TERSE         Print terse output (that generally tries to fit the
                        screen width). [env var: NETDOT_CLI_TERSE] (default:
                        False)
  --server-url SERVER_URL
                        The URL of the Netdot server. [env var:
                        NETDOT_CLI_SERVER_URL] (default:
                        https://nsdb.uoregon.edu)
  --truncate-min TRUNCATE_MIN_CHARS
                        The absolute minimum number of characters to print
                        before truncating. [env var:
                        NETDOT_CLI_TRUNCATE_MIN_CHARS] (default: 20)
  --terse-col-width TERSE_COL_WIDTH
                        The number of characters to use for each column when
                        printing terse output. [env var:
                        NETDOT_CLI_TERSE_COL_WIDTH] (default: 16)
  --terse-max-chars TERSE_MAX_CHARS
                        The maximum number of characters to print before
                        truncating. [env var: NETDOT_CLI_TERSE_MAX_CHARS]
                        (default: None)
  --display-full-objects DISPLAY_FULL_OBJECTS
                        Display the full objects instead of just the object
                        IDs. [env var: NETDOT_CLI_DISPLAY_FULL_OBJECTS]
                        (default: False)
  --skip-ssl SKIP_SSL   Skip SSL verification when making API requests.
                        **Never recommended in production.** Note: you must
                        reconnecting to Netdot for config to take effect.
                        (Used as a default arg for an __init__ method) [env
                        var: NETDOT_CLI_SKIP_SSL] (default: False)
  --connect-timeout CONNECT_TIMEOUT
                        The number of seconds to wait for connection to
                        establish with the Netdot server. Note: you must
                        reconnecting to Netdot for config to take effect.
                        (Used as a default arg for an __init__ method) [env
                        var: NETDOT_CLI_CONNECT_TIMEOUT] (default: 3)
  --timeout TIMEOUT     The number of seconds to wait for a response from the
                        API server. Note: you must reconnecting to Netdot for
                        config to take effect. (Used as a default arg for an
                        __init__ method) Note: "timeout is not a time limit on
                        the entire response download; rather, an exception is
                        raised if the server has not issued a response for
                        timeout seconds (more precisely, if no bytes have been
                        received on the underlying socket for timeout
                        seconds). If no timeout is specified explicitly,
                        requests do not time out." (from
                        requests.readthedocs.io) [env var: NETDOT_CLI_TIMEOUT]
                        (default: 20)
  --raise-parse-errors RAISE_FIELD_PARSE_ERRORS
                        Raise an exception if there is an error parsing any
                        server response (from Netdot). Else, log a warning and
                        continue, using the 'raw string' data. (These are
                        generally warnings that should be fixed by a netdot
                        python package developer) [env var:
                        NETDOT_CLI_RAISE_FIELD_PARSE_ERRORS] (default: False)
  --warn-missing-fields WARN_MISSING_FIELDS
                        Warn if a field is missing from the response from the
                        API server. [env var: NETDOT_CLI_WARN_MISSING_FIELDS]
                        (default: True)
  --threads THREADS     The number of threads to use when making
                        parallelizable API GET requests. Note: you must
                        reconnecting to Netdot for config to take effect.
                        (Used as a default arg for an __init__ method) [env
                        var: NETDOT_CLI_THREADS] (default: 1)
  --trace-downloads TRACE_DOWNLOADS
                        Intermittently log an "INFO" message saying how many
                        bytes have been downloaded from Netdot. Useful for
                        long-running download tasks. (Note: This *is* thread-
                        safe.) Note: you must reconnecting to Netdot for
                        config to take effect. (Used as a default arg for an
                        internal __init__ method) [env var:
                        NETDOT_CLI_TRACE_DOWNLOADS] (default: False)
  --trace-threshold TRACE_THRESHOLD
                        See TRACE_DOWNLOADS above. This threshold determines
                        how often messages should be logged -- the number of
                        bytes downloaded from Netdot before a log message is
                        printed. Note: you must reconnecting to Netdot for
                        config to take effect. (Used as a default arg for an
                        internal __init__ method) [env var:
                        NETDOT_CLI_TRACE_THRESHOLD] (default: 1000000)
  --save-as-file-on-error SAVE_AS_FILE_ON_ERROR
                        (Try to) Save the proposed changes to a file when an
                        error occurs. [env var:
                        NETDOT_CLI_SAVE_AS_FILE_ON_ERROR] (default: True)
  --error-pickle-filename ERROR_PICKLE_FILENAME
                        The filename to use when saving proposed changes to a
                        file when an error occurs. (timestamp based on when
                        the script is run) [env var:
                        NETDOT_CLI_ERROR_PICKLE_FILENAME] (default: netdot-
                        cli-0.4.2-proposed_changes-2024-02-07_08-11.pickle)

 In general, command-line values override environment variables which override
defaults.


⚠ NOTICE: These defaults are read from Environment Variables when 
`netdot.config` module is imported (via `netdot.config.parse_env_vars`). 
Look for "[env var: NETDOT_CLI_...]" above to discover the available 
Environment Variables.

Example: `export NETDOT_CLI_TERSE=True`

Import Env Vars anytime by calling: `netdot.config.parse_env_vars()`

Alternately, override these defaults by setting 
`netdot.config.<ENV_VAR_NAME>` directly in your Python code.

Example: `netdot.config.TERSE=True`

```
