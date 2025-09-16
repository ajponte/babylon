package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	"babylon/data_loader/apiClient"
)

func main() {
	// Create a new API client.
	// We'll use a dummy base URL since this is for demonstration.
	client, err := apiClient.NewAPIClient(&http.Client{}, "http://localhost:5003/api")
	if err != nil {
		log.Fatalf("Failed to create API client: %v", err)
	}

	// Create a context with a timeout.
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// --- Test the Echo endpoint ---
	fmt.Println("--- Testing /echo endpoint ---")
	echoInput := "helloworld"
	resp, echoResp, err := client.DoEcho(ctx, echoInput)
	if err != nil {
		log.Printf("Error calling Echo API: %v", err)
	} else {
		fmt.Printf("Echo API Response: %+v, Status: %s\n", *echoResp, resp.Status)
	}
	fmt.Println()

	// 	// --- Test the Add Transaction endpoint ---
	// 	fmt.Println("--- Testing PUT /history/transaction endpoint ---")
	// 	newTransaction := apiClient.Transaction{
	// 		TransactionType:   "ingress",
	// 		TransactionSource: "SALARY",
	// 		DatePosted:        "2025-09-15",
	// 		Description:       "Monthly salary",
	// 		Amount:            5000.00,
	// 	}
	// 	resp, addTxnResp, err := client.AddTransaction(ctx, newTransaction)
	// 	if err != nil {
	// 		log.Printf("Error calling AddTransaction API: %v", err)
	// 	} else {
	// 		fmt.Printf("AddTransaction API Response: %+v, Status: %s\n", *addTxnResp, resp.Status)
	// 	}
	// 	fmt.Println()

	// 	// --- Test the Get Transaction by ID endpoint ---
	// 	fmt.Println("--- Testing GET /history/transaction endpoint ---")
	// 	// Using a dummy ID for this example.
	// 	transactionID := "f7bf189b-e7c2-4f85-bf73-0c45e7825a74"
	// 	transactionType := "ingress"
	// 	resp, getTxnResp, err := client.GetTransactionById(ctx, transactionID, transactionType)
	// 	if err != nil {
	// 		log.Printf("Error calling GetTransactionById API: %v", err)
	// 	} else {
	// 		fmt.Printf("GetTransactionById API Response: %+v, Status: %s\n", *getTxnResp, resp.Status)
	// 	}
	// 	fmt.Println()

	// 	// --- Test the Get Transaction History endpoint ---
	// 	fmt.Println("--- Testing GET /history/transactions/{transactionType} endpoint ---")
	// 	historyType := "egress"
	// 	// Example timestamps: Start of day today, end of day today.
	// 	// In a real scenario, you'd use a real timestamp range.
	// 	now := time.Now().UTC()
	// 	startTS := now.Add(-24 * time.Hour).Unix()
	// 	endTS := now.Unix()

	// resp, historyResp, err := client.GetTransactionHistory(ctx, historyType, startTS, endTS)
	//
	//	if err != nil {
	//		log.Printf("Error calling GetTransactionHistory API: %v", err)
	//	} else {
	//
	//		fmt.Printf("GetTransactionHistory API Response: %+v, Status: %s\n", *historyResp, resp.Status)
	//	}
	//
	// fmt.Println()
}
