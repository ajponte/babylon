package dataLake

import (
	"context"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// The rest of the code remains the same as previously provided.

// Data represents a single row from the CSV file.
type Data struct {
	Details        string  `bson:"Details"`
	PostingDate    string  `bson:"PostingDate"`
	Description    string  `bson:"Description"`
	Amount         float64 `bson:"Amount"`
	Type           string  `bson:"Type"`
	Balance        float64 `bson:"Balance"`
	CheckOrSlipNum string  `bson:"CheckOrSlipNum"`
}

// SyncLog represents a record in the dataSync collection.
type SyncLog struct {
	CollectionName  string    `bson:"collection_name"`
	SyncTimestamp   time.Time `bson:"sync_timestamp"`
	RecordsUploaded int64     `bson:"records_uploaded"`
}

const (
	// Database and collection names
	dbName        = "babylonDataLake"
	syncTableName = "dataSync"
)

// IngestCSVFiles processes all CSV files in a given directory and uploads them to MongoDB.
func IngestCSVFiles(ctx context.Context, mongoClient *mongo.Client, dirPath string) error {
	// Loop through all files in the directory
	var externalDataSource string
	files, err := os.ReadDir(dirPath)
	if err != nil {
		return fmt.Errorf("failed to read directory: %w", err)
	}

	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".csv") {
			var fileName = file.Name()
			externalDataSource, err = dataSource(fileName)
			if err != nil {
				return fmt.Errorf("failed to retrieve data source")
			}
			filePath := filepath.Join(dirPath, file.Name())
			if err := processCSV(ctx, mongoClient, filePath, externalDataSource); err != nil {
				log.Printf("Error processing file %s: %v", file.Name(), err)
			}
		}
	}
	return nil
}

func processCSV(ctx context.Context, mongoClient *mongo.Client, filePath string, dataSource string) error {
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("failed to open file %s: %w", filePath, err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.FieldsPerRecord = -1 // Allow for a variable number of fields

	// Read the header row
	_, err = reader.Read()
	if err != nil {
		return fmt.Errorf("failed to read CSV header: %w", err)
	}

	var documents []mongo.WriteModel
	var postingDateStr string
	var collectionName string
	var recordsProcessed int64

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return fmt.Errorf("failed to read record from CSV: %w", err)
		}

		// The following are the required fields based on your description.
		const requiredFields = 4 // posting date, description, amount, and at least details to check for consistency

		// Ensure the record has at least the minimum required fields.
		if len(record) < requiredFields {
			log.Printf("Skipping invalid record with less than %d columns in file %s", requiredFields, filePath)
			continue
		}

		// Parse the date
		postingDateStr = record[1]
		parsedDate, err := time.Parse("01/02/2006", postingDateStr)
		if err != nil {
			log.Printf("Skipping record with invalid date format '%s': %v", postingDateStr, err)
			continue
		}

		collectionName = fmt.Sprintf("%s-data-%s", dataSource, parsedDate.Format("2006-01-02"))

		// Parse amount and balance as float64, with a safeguard for missing fields.
		var amount float64
		if len(record) > 3 {
			amount, err = strconv.ParseFloat(record[3], 64)
			if err != nil {
				log.Printf("Skipping record with invalid amount '%s': %v", record[3], err)
				continue
			}
		}

		var balance float64
		if len(record) > 5 {
			balance, err = strconv.ParseFloat(record[5], 64)
			if err != nil {
				log.Printf("Skipping record with invalid balance '%s': %v", record[5], err)
				continue
			}
		}

		doc := Data{
			Details:        record[0],
			PostingDate:    postingDateStr,
			Description:    record[2],
			Amount:         amount,
			Type:           safeGet(record, 4),
			Balance:        balance,
			CheckOrSlipNum: safeGet(record, 6),
		}

		// Create upsert model for the document
		filter := bson.M{"Details": doc.Details, "PostingDate": doc.PostingDate, "Description": doc.Description}
		update := bson.M{"$set": doc}
		upsertModel := mongo.NewUpdateOneModel().
			SetFilter(filter).
			SetUpdate(update).
			SetUpsert(true)
		documents = append(documents, upsertModel)
		recordsProcessed++
	}

	if len(documents) == 0 {
		return fmt.Errorf("no valid documents found in file %s", filePath)
	}

	collection := mongoClient.Database(dbName).Collection(collectionName)

	// Upsert the documents in bulk
	result, err := collection.BulkWrite(ctx, documents, options.BulkWrite().SetOrdered(false))
	if err != nil {
		return fmt.Errorf("failed to perform bulk write for collection %s: %w", collectionName, err)
	}

	log.Printf("Successfully upserted %d documents into collection '%s'.", result.UpsertedCount, collectionName)

	// Insert sync log entry
	syncCollection := mongoClient.Database(dbName).Collection(syncTableName)
	syncLog := SyncLog{
		CollectionName:  collectionName,
		SyncTimestamp:   time.Now(),
		RecordsUploaded: recordsProcessed, // Use the total number of records processed
	}

	_, err = syncCollection.InsertOne(ctx, syncLog)
	if err != nil {
		return fmt.Errorf("failed to insert into dataSync collection: %w", err)
	}

	return nil
}

// safeGet safely retrieves a string from a slice at a given index, returning an empty string if the index is out of bounds.
func safeGet(slice []string, index int) string {
	if index < len(slice) {
		return slice[index]
	}
	return ""
}

// ConnectToMongoDB establishes a connection to the MongoDB database.
func ConnectToMongoDB(ctx context.Context, uri string) (*mongo.Client, error) {
	clientOptions := options.Client().ApplyURI(uri)
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MongoDB: %w", err)
	}

	// Ping the database to verify connection
	err = client.Ping(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to ping MongoDB: %w", err)
	}

	return client, nil
}

func dataSource(dataSourceFileName string) (string, error) {
	var parsedName string
	if strings.ContainsAny(strings.ToLower(dataSourceFileName), "chase") {
		parsedName = "chase"
	} else {
		return "", fmt.Errorf("unable to find a relevant data source for the CSV filename: %s", dataSourceFileName)
	}
	return parsedName, nil
}
