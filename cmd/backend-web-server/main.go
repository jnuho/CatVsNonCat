package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/golang/glog"
	"github.com/jnuho/simpledl/backend/web"
	"github.com/joho/godotenv"
)

const (
	YYYYMMDD  = "2006-01-02"
	HHMMSS24h = "15:04:05"
)

func main() {
	// context and cancel for graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// channel for signaling when the program completes or encounters an error.
	done := make(chan error)

	// Load environment variables
	// -> to be used in `backend/web/util.go` and `pkg/weatherapi.go`
	go func() {
		if err := godotenv.Load(); err != nil {
			done <- fmt.Errorf("error loading .env file: %v", err)
			cancel()
		}
	}()

	// Command-line flags and parse them
	host := flag.String("web-host", ":3001", "Specify host and port for backend.")
	flag.Parse()

	// Logging configuration
	log.SetPrefix(time.Now().Format(YYYYMMDD+" "+HHMMSS24h) + ": ")
	log.SetFlags(log.Lshortfile)

	// Start server in a separate goroutine
	go func() {
		web.StartServer(ctx, *host, done)
	}()

	// Handle OS signals for graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Wait for multiple channels to send data or close.
	// Whichever event occurs first will be handled by the corresponding case block.
	select {
	// 1. Error from the web server (done channel).
	case err := <-done:
		if err != nil {
			glog.Fatal(err)
			log.Printf("`done` channel error!")
		}
	// 2. OS signal (e.g., SIGINT, SIGTERM) received on the sigChan channel.
	case sig := <-sigChan:
		log.Printf("Received signal: %v. Shutting down...", sig)
		cancel()
	// 3. Cancellation of the context (ctx.Done())
	case <-ctx.Done():
		log.Printf("Context cancelled")
	}
}
