## Babylon Data Loader
Load data for babylon.

## Prerequisites
- `go 1.24.4`

- `GNU Make 3.81`

- `mongodb` [driver for `go`](http://github.com/mongodb/mongo-go-driver)

## Building and Running
`make build` → compiles binary at bin/data-loader

`make run` → runs your main.go

`make test` → runs unit tests with coverage

`make cover` → prints coverage summary

`make cover-html` → opens coverage report in browser

`make clean` → removes coverage output

`make tidy` → cleans up go.mod/go.sum

