FROM golang:1.22.5-alpine AS build

WORKDIR /app

COPY go.mod .
COPY cmd cmd

RUN go mod download && go mod verify
RUN go build -o hello cmd/hello

# new image
FROM alpine:latest

COPY --from=build /app/hello /usr/local/bin/hello

EXPOSE 8080

CMD ["hello"]
