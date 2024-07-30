FROM golang:1.22.3-alpine AS build

WORKDIR /app

COPY go.mod go.sum ./
COPY cmd cmd

RUN go mod download && go mod verify
RUN go build -o hello ./cmd/hello

# new image
FROM alpine:latest

COPY --from=build /app/hello /usr/local/bin/hello

EXPOSE 8080

CMD ["hello"]
