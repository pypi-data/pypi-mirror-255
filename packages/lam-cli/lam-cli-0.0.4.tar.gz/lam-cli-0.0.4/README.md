# lam

Lam is a `jq` transpiling tool for Laminar.

## Quickstart

Install the dependencies.

```bash
brew install jq
# or
sudo apt-get install jq
make setup
```

Run the CLI tool.

> Note: ARGS is used to pass arguments to the CLI tool via `make`.

```bash
make cli ARGS="<program> <input>"
```

## Install

Install in Dockerfile with:

```
RUN pip3 install git+https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/user/project.git@{version}
```

### Examples

```bash
make cli ARGS="run test/simple/program.lam test/simple/data.json"
```

Run the `test/simple` example, it should return:

```json
{
  "value": 6
}
{
  "value": 8
}
{
  "value": 9
}
```

## Setup (manual)

Create a virtual environment and install the dependencies.

```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

Running the CLI tool.

```bash
python3 ./lam/lam.py run <program> <input>
```

## Dependencies

Make sure to update the `requirements.txt` file when adding new dependencies.

```bash
pip3 install <package>
pip3 freeze > requirements.txt
```