<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: MIT
-->

# bovine_herd

`bovine_herd` is a `bovine` powered Fediverse server, which interoperates with the rest of the FediVerse.
Please consult [the documentation](https://bovine-herd.readthedocs.io/en/latest/) for details to
run bovine_herd.

The simplest bovine_herd Fediverse server would be given by

```python
from quart import Quart

from bovine_herd import BovineHerd

app = Quart(__name__)
BovineHerd(app)
```

by running `hypercorn app:app` one can then start a server. This server does not
provide a user interface nor any users.
To add users, one can use [bovine-tool](https://pypi.org/project/bovine-tool/).
With the default configuration, these will be stored in `bovine.sqlite3`.

One should note that while `bovine_herd` should be domain agnostic, so the same
instance can serve any domain, created users are not.
