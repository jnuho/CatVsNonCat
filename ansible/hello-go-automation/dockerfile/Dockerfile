FROM golang:1.22.3-alpine AS build

WORKDIR /app

COPY cmd cmd

RUN go build cmd/hello/main.go

# new image
FROM alpine:latest

WORKDIR /app
COPY --from=build /app/hello /app/hello

EXPOSE 8080

CMD ["hello"]
