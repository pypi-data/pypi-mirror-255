# transformer.bee Client (Python)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Versions (officially) supported](https://img.shields.io/pypi/pyversions/transformerbeeclient.svg)
![Unittests status badge](https://github.com/Hochfrequenz/TransformerBeeClient.py/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/TransformerBeeClient.py/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/TransformerBeeClient.py/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/TransformerBeeClient.py/workflows/Formatting/badge.svg)
![PyPi Status Badge](https://img.shields.io/pypi/v/transformerbeeclient)

This library is a Python HTTP client for transformer.bee aka edifact-bo4e-converter.
We also maintain a [.NET version](https://github.com/Hochfrequenz/TransformerBeeClient.NET) of this client.

It allows you to convert EDIFACT messages to BO4E and vice versa by speaking to Hochfrequenz's transformer.bee service.
Note that the actual conversion happens in the transformer.bee service/backend, this library only provides a convenient way to use its API.

## How to use this library

### Prerequisites / Account

First of all, you need an account to use transformer.bee.
Ask info@hochfrequenz.de or ping [@JoschaMetze](https://github.com/joschametze) on GitHub to get one.

You can check if your account is working by logging [into our stage environment](https://transformerstage.utilibee.io/app/).

### Using the client
Install the library via [pip](https://pypi.org/project/transformerbeeclient/):
```bash
pip install transformerbeeclient
```

### Authentication
As of 2024-02-06 we support either no authentication or OAuth2 client ID/client secret authentication.
Both the unauthenticated and the authenticated client implement the `TransformerBeeClient` protocol, so you can use them interchangeably.

#### No Authentication
If you're hosting transformer.bee in the same network or your localhost and there is no authentication, you can instantiate the client
```python
from yarl import URL
from transformerbeeclient.client import UnauthenticatedTransformerBeeClient

client = UnauthenticatedTransformerBeeClient(base_url=URL("http://localhost:5021"))
```

#### OAuth2 with Client ID/Client Secret
If, which is more likely, Hochfrequenz provided you with a client Id and secret, you can use the `AuthenticatedTransformerBeeClient` class like this:
```python
from yarl import URL
from transformerbeeclient import AuthenticatedTransformerBeeClient

client = AuthenticatedTransformerBeeClient(
    base_url=URL("https://transformer.utilibee.io"),
    client_id="your_client_id",
    client_secret="your_client_secret",
)
```

#### Minimal Working Examples
Find full examples of both conversions in [the integration tests](integrationtests/test_conversion.py).
Find the respective BO4E and EDIFACTs in [the test data folder](integrationtests/TestEdifact).

### Conversion
There are two main methods to convert between EDIFACT and BO4E:
- `edifact_to_bo4e`
- `bo4e_to_edifact`

Both have an `EdifactFormatVersion` as argument (imported from [maus](https://github.com/Hochfrequenz/mig_ahb_utility_stack)), which denotes which version of the EDIFACT format you want to use.
We group all the different versions of the EDIFACT format into an enum, so you can easily choose the one you need.
E.g. `EdifactFormatVersion.FV2310` stands for all MIG/AHB versions valid since 2023-10-01.


#### Convert EDIFACT to BO4E
```python
from maus.edifact import EdifactFormatVersion
# client instantiation goes here

bo4e = await client.edifact_to_bo4e("UNA:+,? 'UNB...", EdifactFormatVersion.FV2310)
```

#### Convert BO4E to EDIFACT
```python
from maus.edifact import EdifactFormatVersion
from transformerbeeclient.models.boneycomb import BOneyComb
# client instantiation goes here

boney_comb = BOneyComb.model_validate({"stammdaten":[...], "transaktionsdaten":{...}})
edifact = await client.bo4e_to_edifact(boney_comb, EdifactFormatVersion.FV2310)
```

## Development
For development of this library, follow the instructions in our [Python Template Repository](https://github.com/Hochfrequenz/python_template_repository).

### Release (CI/CD)

To release a new version of this library, [create a new release](https://github.com/Hochfrequenz/TransformerBeeClient.py/releases/new) in GitHub.
Make sure its tag starts with `v` and the version number, e.g. `v1.2.3`.
Releases are not restricted to the main branch but we prefer them to happen there.

## Contribute
You are very welcome to contribute to this template repository by opening a pull request against the main branch.

## Related Tools and Context
This repository is part of the [Hochfrequenz Libraries and Tools for a truly digitized market communication](https://github.com/Hochfrequenz/digital_market_communication/).

## Hochfrequenz
[Hochfrequenz Unternehmensberatung GmbH](https://www.hochfrequenz.de) is a Grünwald (near Munich) based consulting company with offices in Berlin and Bremen and attractive remote options.
We're not only a main contributor for open source software for German utilities but, according to [Kununu ratings](https://www.kununu.com/de/hochfrequenz-unternehmensberatung1), also among the most attractive employers within the German energy market. Applications of talented developers are welcome at any time!
Please consider visiting our [career page](https://www.hochfrequenz.de/index.php/karriere/aktuelle-stellenausschreibungen/full-stack-entwickler) (German only).
