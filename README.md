# MkDocs Json FASER plugin

This mkdocs plugin allows to point at a list of json schemas in a remote repository
and have those schemas be parsed into meaningful markdown formatted files for 
insertion into a site via the use of a plugin like [mkdocs-include-markdown-plugin](https://pypi.org/project/mkdocs-include-markdown-plugin/).

This plugin was written expressly for use in the [FASER collaboration]() TDAQ documentation
and so may not be as flexible as you wish.  Pull requests are welcomed!

# Usage
As an example, the configuration
```yaml
  - json:
      url: ssh://git@gitlab.cern.ch:7999/faser/daq.git
      schemas: [configs/schemas/TriggerReceiver.schema, configs/schemas/DigitizerReceiver.schema]

```
will clone the remote repository at `url` and
perform the transformation for each of the schema listed in `schemas`.  It will produce
one `.md` in the same `docs` directory as the other documentation files with the same
base name as the schema.

In this case, the remote `ssh://git@gitlab.cern.ch:7999/faser/daq.git` will be cloned and the two
schemas (`configs/schemas/TriggerReceiver.schema`, `configs/schemas/DigitizerReceiver.schema`)  
will be parsed into `docs/TriggerReceiver.md` and `docs/DigitizerReceiver.md`.

