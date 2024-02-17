Modern and easy-to-use logging configuration library 
inspired by the [tutorial](https://www.youtube.com/@mCoding) by [mCoding](https://www.youtube.com/@mCoding).

## Installation

```bash
pip install grateful-logging 
```


## Usage
Create configuration file
```bash
python -m grateful_logging --file_name=logger-config.json  
# default value of file_name is `logger-config.json`, 
#  you can change it, or not specify if you want to use default
```

Code implementation

```python
import logging
from grateful_logging.configure import GratefulLoggingConfigurator


logger = logging.getLogger("my_app")


def setup_logging():
    GratefulLoggingConfigurator()\
        .setup_logging(file_path="logger-config.json")


def main():
    setup_logging()
    logger.debug("debug message", extra={"x": "hello"})
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("cirtical message")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("exception message")


if __name__ == "__main__":
    main()
    logger.info("info message")

```

