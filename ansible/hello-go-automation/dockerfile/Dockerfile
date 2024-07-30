FROM golang:1.22.3-alpine AS build

WORKDIR /app

COPY cmd cmd

RUN go build -o hello ./cmd/hello

# new image
FROM alpine:latest

COPY --from=build /app/hello /usr/local/bin/hello

EXPOSE 8080

CMD ["hello"]
