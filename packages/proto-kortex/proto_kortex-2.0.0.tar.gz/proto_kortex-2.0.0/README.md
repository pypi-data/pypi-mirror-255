# proto-kortex

Semantically versioned protobufs used to generate client packages and documentation

## Protobuf Documentation

[Link](/docs/README.md)

## Maintaining

Install the pre-commit hook to ensure any changes to the protobuf get refleted in the docs.
Use Buf to lint the proto and detect breaking changes.

## How to use (locally)

CI will automatically generate client packages and documentation for each release.
To run locally:

### Web Client

You should have `make` and `npm` installed for generating the web client.

```bash
$ npm i -g @protobuf-ts/plugin
$ make client-web
```

### Python Client

You'll need `make` and `pip` installed for generating the python client.

```bash
$ make client-python
```

### Create Rust crate

1. Install Buf: https://docs.buf.build/installation
2. Run `make buf-gen`
   - This should output a rust crate in the `gen/crate` directory that will be used by other services, such as Alexandria.
