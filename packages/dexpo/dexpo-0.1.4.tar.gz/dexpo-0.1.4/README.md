# Introduction

**Dexpo** is a simple CLI tool for generating basic reports about a given python package's reputation and known vulnerabilites using data from the [libraries.io API](https://libraries.io) and pypi.org.

**Disclaimer**: Only PyPI projects are currently supported.

# Requirements

- Python >= 3.11.6
- [libraries.io](https://libraries.io) account

# Getting Started

1. Create a [libraries.io](https://libraries.io) account and get your api key from the settings page.
2. You must include your private `--api-key` value as an argument or store it in an environment variable called `LIBRARIESIO_API_KEY`
3. Install dexpo `pip install dexpo`

# Usage

```console
$ dexpo pandas --api-key 123APIKEY456
```
![example](https://github.com/jackboy2fly/dexpo/assets/81083035/62bc80a8-0fa7-468f-8515-0af622e42dc2)
