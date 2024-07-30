package main

import (
    "fmt"
    "log"
    "encoding/json"
    "net/http"
)

// Handler for /health route
func healthHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet {
        http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
        return
    }
    w.Header().Set("Content-Type", "text/plain")
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("ok"))
}

// Handler for /test route
func testHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
        return
    }
    response := map[string]interface{}{
        "status": 200,
    }
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(response)
}

func main() {
    http.HandleFunc("/health", healthHandler)
    http.HandleFunc("/test", testHandler)

    // Start the server on port 8080
    serverAddr := ":8080"
    log.Printf("Server is listening on %s\n", serverAddr)
    if err := http.ListenAndServe(serverAddr, nil); err != nil {
        log.Fatalf("Could not listen on port %s %v", serverAddr, err)
    }
}

