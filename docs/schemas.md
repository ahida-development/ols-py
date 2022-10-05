# Request/Response schemas

We validate request parameters and responses
with [pydantic](https://pydantic-docs.helpmanual.io)
to try and provide more certainty about the
data sent and received from the OLS API. This should also
mean you get useful type annotations when working
with the client in your own code
(you may want to install a Pydantic plugin for
your IDE/editor, e.g. [VS Code](https://pydantic-docs.helpmanual.io/visual_studio_code/)).


## :::ols_py.schemas.requests
    options:
      show_bases: false

## :::ols_py.schemas.responses
    options:
      show_bases: false
