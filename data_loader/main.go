// main.go
package main

import (
	datalake "babylon/data_loader/datalake"
	"context"
	"log/slog" // Change this import from "log" to "log/slog"
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
	// 1. Create a logger at the main entry point
	logger := slog.New(slog.NewTextHandler(os.Stdout, nil))

	// Create a new context and inject the logger into it
	ctx, cancel := context.WithTimeout(
		datalake.WithLogger(context.Background(), logger),
		defaultTimeoutSeconds*time.Second,
	)
	defer cancel()

	mongoURI := os.Getenv(envMongoURI)
	if mongoURI == "" {
		mongoURI = defaultMongoURI
		logger.Info(
			"MongoDB URI not found in environment variable, using default",
			"env_var", envMongoURI,
			"uri", defaultMongoURI,
		)
	}

	csvDirectory := os.Getenv(envCSVDirectory)
	if csvDirectory == "" {
		csvDirectory = defaultCSVDir
		logger.Info(
			"CSV directory not found in environment variable, using default",
			"env_var", envCSVDirectory,
			"dir", defaultCSVDir,
		)
	}

	_, err := os.Stat(csvDirectory)
	if err != nil || os.IsNotExist(err) {
		logger.Error(
			"The directory does not exist. Please create it and place your CSV files inside.",
			"dir", csvDirectory,
			"error", err,
		)
		os.Exit(1)
	}

	client, err := datalake.ConnectToMongoDB(ctx, mongoURI)
	if err != nil {
		logger.Error("Failed to connect to MongoDB", "error", err)
		os.Exit(1)
	}

	defer func() {
		err = client.Disconnect(ctx)
		if err != nil {
			logger.Error("Error disconnecting from MongoDB", "error", err)
		}
	}()

	logger.Info("Successfully connected to MongoDB.")

	err = datalake.IngestCSVFiles(ctx, client, csvDirectory)
	if err != nil {
		logger.Error("Error ingesting CSV files", "error", err)
		os.Exit(1)
	}

	logger.Info("Data ingestion process completed successfully.")
}
