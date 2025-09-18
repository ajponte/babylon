package main

import (
	"context"
	"log"
	"os"
	"time"
)

const (
	// Default values if environment variables are not set
	defaultMongoURI = "mongodb://localhost:27017"
	defaultCSVDir   = "./data"
	envMongoURI     = "MONGO_URI"
	envCSVDirectory = "CSV_DIR"
)

func main() {
	// Read MongoDB URI from environment variable, fallback to default
	mongoURI := os.Getenv(envMongoURI)
	if mongoURI == "" {
		mongoURI = defaultMongoURI
		log.Printf("MongoDB URI not found in environment variable '%s', using default: %s", envMongoURI, defaultMongoURI)
	}

	// Read CSV directory from environment variable, fallback to default
	csvDirectory := os.Getenv(envCSVDirectory)
	if csvDirectory == "" {
		csvDirectory = defaultCSVDir
		log.Printf("CSV directory not found in environment variable '%s', using default: %s", envCSVDirectory, defaultCSVDir)
	}

	// Create a context with a timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Check if the data directory exists.
	if _, err := os.Stat(csvDirectory); os.IsNotExist(err) {
		log.Fatalf("Error: The directory '%s' does not exist. Please create it and place your CSV files inside.", csvDirectory)
	}

	// Connect to MongoDB
	client, err := ConnectToMongoDB(ctx, mongoURI)
	if err != nil {
		log.Fatalf("Failed to connect to MongoDB: %v", err)
	}
	defer func() {
		if err = client.Disconnect(ctx); err != nil {
			log.Fatalf("Error disconnecting from MongoDB: %v", err)
		}
	}()

	log.Println("Successfully connected to MongoDB.")

	// Ingest CSV files from the specified directory
	err = IngestCSVFiles(ctx, client, csvDirectory)
	if err != nil {
		log.Fatalf("Error ingesting CSV files: %v", err)
	}

	log.Println("Data ingestion process completed successfully.")
}
