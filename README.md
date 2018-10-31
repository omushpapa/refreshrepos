# Refresh Repos

Refreshes repositories in a certain directory

# Usage

## Requirements

1. Python 3 (Tested with 3.5/6)

2. [Pip](https://bootstrap.pypa.io/get-pip.py)

3. [Pipenv](https://pipenv.readthedocs.io/) (optional)


## Usage

1. Install environment requirements using `pip3 install --user -r requirements.txt` or using `pipenv install`

2. Edit [settings.ini](settings.ini) and replace `username` with your account username (optional).

3. Make `refresh.py` executable using `sudo chmod +x refresh.py`

4. Run `refresh.py --username <username> /path/to/parent/directory/of/repositories`
