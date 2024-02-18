# Cool-Testing-Timing
Cool Testing - timing. Cool testing lib is an set of tools for developers which would help them with building metrics for software develop.


## CT Timing Decorator :stopwatch:

Enhance your Python applications with precise function execution timing! The CT Timing Decorator is a Python library designed to make performance monitoring a breeze. Wrap any function to log its execution time, improving debugging and optimization without the hassle of manual timing code.

## :sparkles: Features


Easy Integration - Just a decorator away from timing any function.

Automatic Logging - Logs start, end, and elapsed time with beautiful formatting.

Zero Dependency - Utilizes only Python's standard library.

## :arrow_down: Install

### :package: PyPI

```bash


pip install ct-timing
```


### :computer: Install Locally (From GitHub)

For those who prefer the bleeding-edge version or want to contribute to the development, you can install the library directly from GitHub:

Clone the Repository:

```bash

git clone https://github.com/Kotmin/Cool-Testing-Timing.git
cd ct-timing
```
Install Using Pip:

```bash

pip install .
```
This approach installs the library from the source code, ensuring you have the latest changes or can work on developing new features or fixes.
## :star: Live Stats
Section under construction
## :rocket: Quick Start

To use the CT Timing Decorator, import the timing decorator from the ct.timing package and apply it to any function:

```python

from ct.timing import timing

@timing
def my_function():
    # Your function logic here
    pass
```
Run your decorated function as usual and observe detailed timing logs automatically!
## :mag: Overview

Why choose CT Timing Decorator over traditional time.start() and time.end() approaches? Simplicity and efficiency. Our decorator abstracts away the boilerplate timing code, allowing you to focus on what matters: your application logic. Additionally, it provides consistent, formatted output that is both human-readable and easy to parse programmatically.
### :heavy_check_mark: Benefits over Manual Timing

  - No More Boilerplate: Forget about starting and stopping timers manually.
  - Automatic Logging: Get formatted, easy-to-read logs without extra code.
  - Consistency: Uniform timing and logging logic across all your functions.

## :wrench: Additional Settings

CT Timing Decorator comes with a few knobs to tweak:

    Custom Logging Function: Override the default logger to integrate with your application's logging system.
    Time Format Customization: Change how the elapsed time is displayed to suit your needs.

```python

from ct.timing import timing, set_custom_logger, set_time_format

# Set a custom logger
set_custom_logger(my_custom_logger)

# Customize the time format
set_time_format("%H:%M:%S")
```
For more advanced usage and contributions, please refer to our GitHub repository.
## :heart: Support

Found a bug? Have an idea for improvement? Contributions are welcome! Please open an issue or submit a pull request.
