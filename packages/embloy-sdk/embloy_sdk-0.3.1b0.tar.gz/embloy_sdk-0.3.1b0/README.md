# Embloy Python

Embloy's Python SDK for interacting with your Embloy integration.

## Usage

Install Embloy-Node SDK:

```Bash
# Install through pip
pip3 install --upgrade embloy_sdk
```

or in your requirements.txt
```python
# Find the version you want to pin:
# https://pypi.org/project/embloy-sdk/#history
# Specify that version in your requirements.txt file
embloy_sdk>=0.3.1b
```

Integrate it in your service:

```Python
# In your application or script
from embloy_sdk import EmbloyClient, EmbloySession

# Replace with your actual values
client_token = 'your_client_token'
session = EmbloySession("job", "your_job_slug", "your_success_url", "your_cancel_url")

# Make a request to the Embloy API
redirect_url = EmbloyClient(client_token, session).make_request()
```

## Publish Package
```Bash
python setup.py sdist bdist_wheel

twine upload dist/*
```

---

© Carlo Bortolan, Jan Hummel

> Carlo Bortolan &nbsp;&middot;&nbsp;
> GitHub [@carlobortolan](https://github.com/carlobortolan) &nbsp;&middot;&nbsp;
> contact via [bortolanoffice@embloy.com](mailto:bortolanoffice@embloy.com)
>
> Jan Hummel &nbsp;&middot;&nbsp;
> GitHub [@github4touchdouble](https://github.com/github4touchdouble) &nbsp;&middot;&nbsp;
> contact via [hummeloffice@embloy.com](mailto:hummeloffice@embloy.com)

