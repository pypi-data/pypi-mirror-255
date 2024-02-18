LocalStack Lambda AppConfig Extension
=============================================

This is a simple extension to enable the Lambda AppConfig extension in LocalStack: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-integration-lambda-extensions.html

## Installation

Details following soon ...

## Development

Run the following commands, with a LocalStack Pro instance running:
```
$ make install
$ make build
$ make enable
# to restart the main process and load the extension:
$ docker exec localstack_main kill -sSIGUSR1 1
```

## Change Log

* `v0.1.0`: Initial release

## License

(c) 2023+ LocalStack
