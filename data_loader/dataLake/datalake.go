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
	dbName        = "babylonDataLake"
	syncTableName = "dataSync"
)

// ---- Abstractions for Testability ----

type dataStore interface {
	BulkWrite(ctx context.Context, models []mongo.WriteModel, opts ...*options.BulkWriteOptions) (*mongo.BulkWriteResult, error)
	InsertOne(ctx context.Context, document interface{}, opts ...*options.InsertOneOptions) (*mongo.InsertOneResult, error)
}

type collectionProvider interface {
	Collection(name string) dataStore
}

// mongoCollection adapts *mongo.Collection to dataStore.
type mongoCollection struct {
	*mongo.Collection
}

func (c *mongoCollection) BulkWrite(ctx context.Context, models []mongo.WriteModel, opts ...*options.BulkWriteOptions) (*mongo.BulkWriteResult, error) {
	return c.Collection.BulkWrite(ctx, models, opts...)
}

func (c *mongoCollection) InsertOne(ctx context.Context, document interface{}, opts ...*options.InsertOneOptions) (*mongo.InsertOneResult, error) {
	return c.Collection.InsertOne(ctx, document, opts...)
}

// mongoProvider adapts *mongo.Client to collectionProvider.
type mongoProvider struct {
	client *mongo.Client
}

func (p *mongoProvider) Collection(name string) dataStore {
	return &mongoCollection{p.client.Database(dbName).Collection(name)}
}

// ---- Core Logic ----

// IngestCSVFiles processes all CSV files in a given directory and uploads them to MongoDB.
func IngestCSVFiles(ctx context.Context, client *mongo.Client, dirPath string) error {
	files, err := os.ReadDir(dirPath)
	if err != nil {
		return fmt.Errorf("failed to read directory: %w", err)
	}

	provider := &mongoProvider{client: client}

	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".csv") {
			externalDataSource, err := dataSource(file.Name())
			if err != nil {
				return fmt.Errorf("failed to retrieve data source: %w", err)
			}
			filePath := filepath.Join(dirPath, file.Name())
			if err := ProcessCSV(ctx, provider, filePath, externalDataSource); err != nil {
				log.Printf("Error processing file %s: %v", file.Name(), err)
			}
		}
	}
	return nil
}

// ProcessCSV reads a CSV file from a given path and uploads the data to MongoDB.
func ProcessCSV(ctx context.Context, provider collectionProvider, filePath string, dataSource string) error {
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("failed to open file %s: %w", filePath, err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.FieldsPerRecord = -1

	// Skip header
	if _, err = reader.Read(); err != nil {
		return fmt.Errorf("failed to read CSV header: %w", err)
	}

	var documents []mongo.WriteModel
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

		if len(record) < 4 {
			log.Printf("Skipping invalid record with less than 4 columns in file %s", filePath)
			continue
		}

		postingDateStr := record[1]
		parsedDate, err := time.Parse("01/02/2006", postingDateStr)
		if err != nil {
			log.Printf("Skipping record with invalid date format '%s': %v", postingDateStr, err)
			continue
		}

		collectionName = fmt.Sprintf("%s-data-%s", dataSource, parsedDate.Format("2006-01-02"))

		amount, _ := strconv.ParseFloat(record[3], 64)
		balance := 0.0
		if len(record) > 5 {
			balance, _ = strconv.ParseFloat(record[5], 64)
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

		filter := bson.M{"Details": doc.Details, "PostingDate": doc.PostingDate, "Description": doc.Description}
		update := bson.M{"$set": doc}
		upsertModel := mongo.NewUpdateOneModel().SetFilter(filter).SetUpdate(update).SetUpsert(true)

		documents = append(documents, upsertModel)
		recordsProcessed++
	}

	if len(documents) == 0 {
		return fmt.Errorf("no valid documents found in file %s", filePath)
	}

	collection := provider.Collection(collectionName)
	result, err := collection.BulkWrite(ctx, documents, options.BulkWrite().SetOrdered(false))
	if err != nil {
		return fmt.Errorf("failed to perform bulk write for collection %s: %w", collectionName, err)
	}

	log.Printf("Successfully upserted %d documents into collection '%s'.", result.UpsertedCount, collectionName)

	syncCollection := provider.Collection(syncTableName)
	syncLog := SyncLog{
		CollectionName:  collectionName,
		SyncTimestamp:   time.Now(),
		RecordsUploaded: recordsProcessed,
	}

	if _, err = syncCollection.InsertOne(ctx, syncLog); err != nil {
		return fmt.Errorf("failed to insert into dataSync collection: %w", err)
	}

	return nil
}

// safeGet retrieves slice[index] safely.
func safeGet(slice []string, index int) string {
	if index < len(slice) {
		return slice[index]
	}
	return ""
}

// ConnectToMongoDB establishes a connection to MongoDB.
func ConnectToMongoDB(ctx context.Context, uri string) (*mongo.Client, error) {
	clientOptions := options.Client().ApplyURI(uri)
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MongoDB: %w", err)
	}
	if err = client.Ping(ctx, nil); err != nil {
		return nil, fmt.Errorf("failed to ping MongoDB: %w", err)
	}
	return client, nil
}

func dataSource(fileName string) (string, error) {
	if strings.Contains(strings.ToLower(fileName), "chase") {
		return "chase", nil
	}
	return "", fmt.Errorf("unable to find a relevant data source for the CSV filename: %s", fileName)
}
