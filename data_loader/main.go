// DataLoader main entry point.
package main

import (
	datalake "babylon/data_loader/datalake"
	"context"
	"log"
	"os"
	"time"
)

const (
	defaultTimeoutSeconds = 30
	defaultMongoURI       = "mongodb://localhost:27017"
	defaultCSVDir         = "./data"
	envMongoURI           = "MONGO_URI"
	envCSVDirectory       = "CSV_DIR"
)

func main() {
	mongoURI := os.Getenv(envMongoURI)
	if mongoURI == "" {
		mongoURI = defaultMongoURI
		log.Printf("MongoDB URI not found in environment variable '%s', using default: %s", envMongoURI, defaultMongoURI)
	}

	csvDirectory := os.Getenv(envCSVDirectory)
	if csvDirectory == "" {
		csvDirectory = defaultCSVDir
		log.Printf("CSV directory not found in environment variable '%s', using default: %s", envCSVDirectory, defaultCSVDir)
	}

	ctx, cancel := context.WithTimeout(context.Background(), defaultTimeoutSeconds*time.Second)
	defer cancel()

	if _, err := os.Stat(csvDirectory); os.IsNotExist(err) {
		log.Fatalf("Error: The directory '%s' does not exist. Please create it and place your CSV files inside.", csvDirectory)
	}

	// Call the function from the datalake package
	client, err := datalake.ConnectToMongoDB(ctx, mongoURI)
	if err != nil {
		log.Fatalf("Failed to connect to MongoDB: %v", err)
	}

	defer func() {
		if err = client.Disconnect(ctx); err != nil {
			log.Fatalf("Error disconnecting from MongoDB: %v", err)
		}
	}()

	log.Println("Successfully connected to MongoDB.")

	// Call the function from the datalake package
	err = datalake.IngestCSVFiles(ctx, client, csvDirectory)
	if err != nil {
		log.Fatalf("Error ingesting CSV files: %v", err)
	}

	log.Println("Data ingestion process completed successfully.")
}
