package apiClient

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
)

const (
	// DefaultBasePath is the default base path for the API client.
	DefaultBasePath = "/api"
)

// APIClient manages all endpoints of the Babylon API.
type APIClient struct {
	// a pointer to the http client to use.
	HttpClient *http.Client
	// a pointer to the url to be used as a base url for all requests.
	BasePath *url.URL
}

// NewAPIClient creates a new APIClient.
func NewAPIClient(httpClient *http.Client, basePath string) (*APIClient, error) {
	// Use a default http client if none is provided.
	if httpClient == nil {
		httpClient = &http.Client{}
	}

	// Parse the base path URL.
	basePathUrl, err := url.Parse(basePath)
	if err != nil {
		return nil, err
	}

	// Return a new APIClient instance.
	return &APIClient{
		HttpClient: httpClient,
		BasePath:   basePathUrl,
	}, nil
}

// Echo represents the response from the Echo endpoint.
type EchoResponse struct {
	// The value that was echoed back.
	EchoedValue string `json:"echoed_value,omitempty"`
}

// HistoryTransaction represents a transaction in the history.
type HistoryTransaction struct {
	// A unique identifier for a transaction.
	Id string `json:"id,omitempty"`
}

type TransactionPutResponse struct {
	TransactionId string `json:"transactionId"`
}

// Transaction represents a single transaction.
type Transaction struct {
	// The type of transaction (ingress or egress).
	TransactionType string `json:"transactionType"`
	// The source of the transaction.
	TransactionSource string `json:"transactionSource"`
	// Date the transaction was posted to an external account.
	DatePosted string `json:"datePosted"`
	// Description of the transaction.
	Description string `json:"description"`
	// Amount posted in the transaction.
	Amount float64 `json:"amount"`
	// Slip number from an external institution.
	SlipNumber string `json:"slipNumber,omitempty"`
}

// TransactionType represents the type of transaction.
type TransactionType string

// UtcTimestamp represents a UNIX UTC timestamp in seconds.
type UtcTimestamp int64

// DebugMessageResponse represents a debug message attached to an HTTP response.
type DebugMessageResponse struct {
	// A message attached to an HTTP response for debugging purposes.
	Message string `json:"message,omitempty"`
}

// TransactionHistoryResponse is a list of transactions.
type TransactionHistorySearchResponse struct {
	Transactions []HistoryTransaction `json:"transactions,omitempty"`
}

// DoEcho sends a GET request to the /echo endpoint.
func (c *APIClient) DoEcho(ctx context.Context, inputVal string) (*http.Response, *EchoResponse, error) {
	// Construct the full URL by combining the base path with the endpoint path.
	localVarPath := c.BasePath.String() + "/echo"

	// Create the request.
	req, err := http.NewRequestWithContext(ctx, "GET", localVarPath, nil)
	if err != nil {
		return nil, nil, fmt.Errorf("error creating request: %w", err)
	}

	// Add query parameters.
	q := req.URL.Query()
	q.Add("inputVal", inputVal)
	req.URL.RawQuery = q.Encode()

	// Add Content-Type header.
	req.Header.Add("Content-Type", "application/json")

	// Send the request.
	resp, err := c.HttpClient.Do(req)
	if err != nil {
		return resp, nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	// Handle response based on status code.
	if resp.StatusCode == http.StatusOK {
		var result EchoResponse
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, nil, fmt.Errorf("error reading response body: %w", err)
		}
		if err = json.Unmarshal(body, &result); err != nil {
			return resp, nil, fmt.Errorf("error unmarshaling response body: %w", err)
		}
		return resp, &result, nil
	} else if resp.StatusCode == http.StatusBadRequest || resp.StatusCode == http.StatusInternalServerError {
		var debugMsg DebugMessageResponse
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, nil, fmt.Errorf("error reading response body for error: %w", err)
		}
		if err = json.Unmarshal(body, &debugMsg); err != nil {
			return resp, nil, fmt.Errorf("error unmarshaling error response body: %w", err)
		}
		return resp, nil, fmt.Errorf("API error: %s", debugMsg.Message)
	}

	return resp, nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
}

// GetTransactionById sends a GET request to the /history/transaction endpoint.
func (c *APIClient) GetTransactionById(ctx context.Context, transactionId string, transactionType string) (*http.Response, *HistoryTransaction, error) {
	// Use ResolveReference to correctly combine the base URL with the endpoint path.
	localVarPath := c.BasePath.ResolveReference(&url.URL{Path: "/history/transaction"})

	// Add query parameters.
	q := url.Values{}
	q.Add("transactionId", transactionId)
	q.Add("transactionType", transactionType)
	localVarPath.RawQuery = q.Encode()

	// Create the request.
	req, err := http.NewRequestWithContext(ctx, "GET", localVarPath.String(), nil)
	if err != nil {
		return nil, nil, fmt.Errorf("error creating request: %w", err)
	}

	// Add Content-Type header.
	req.Header.Add("Content-Type", "application/json")

	// Send the request.
	resp, err := c.HttpClient.Do(req)
	if err != nil {
		return resp, nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	// Handle response based on status code.
	if resp.StatusCode == http.StatusOK {
		var result HistoryTransaction
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, nil, fmt.Errorf("error reading response body: %w", err)
		}
		if err = json.Unmarshal(body, &result); err != nil {
			return resp, nil, fmt.Errorf("error unmarshaling response body: %w", err)
		}
		return resp, &result, nil
	} else if resp.StatusCode >= 400 {
		var debugMsg DebugMessageResponse
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, nil, fmt.Errorf("error reading response body for error: %w", err)
		}
		if err = json.Unmarshal(body, &debugMsg); err != nil {
			return resp, nil, fmt.Errorf("error unmarshaling error response body: %w", err)
		}
		return resp, nil, fmt.Errorf("API error: %s", debugMsg.Message)
	}

	return resp, nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
}

// AddTransaction sends a PUT request to the /history/transaction endpoint.
func (c *APIClient) AddTransaction(ctx context.Context, transaction Transaction) (*http.Response, *TransactionPutResponse, error) {
	// Marshal the request body.
	bodyBytes, err := json.Marshal(transaction)
	if err != nil {
		return nil, nil, fmt.Errorf("error marshaling request body: %w", err)
	}

	// Construct the full URL by combining the base path with the endpoint path.
	localVarPath := c.BasePath.String() + "/history/transaction"

	// Create the request.
	req, err := http.NewRequestWithContext(ctx, "PUT", localVarPath, bytes.NewReader(bodyBytes))
	if err != nil {
		return nil, nil, fmt.Errorf("error creating request: %w", err)
	}

	// Add Content-Type header.
	req.Header.Add("Content-Type", "application/json")

	// Send the request.
	resp, err := c.HttpClient.Do(req)
	if err != nil {
		return resp, nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	// Handle response based on status code.
	if resp.StatusCode == http.StatusCreated {
		var result TransactionPutResponse
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, nil, fmt.Errorf("error reading response body: %w", err)
		}
		if err = json.Unmarshal(body, &result); err != nil {
			return resp, nil, fmt.Errorf("error unmarshaling response body: %w", err)
		}
		return resp, &result, nil
	} else if resp.StatusCode >= 400 {
		var debugMsg DebugMessageResponse
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, nil, fmt.Errorf("error reading response body for error: %w", err)
		}
		if err = json.Unmarshal(body, &debugMsg); err != nil {
			return resp, nil, fmt.Errorf("error unmarshaling error response body: %w", err)
		}
		return resp, nil, fmt.Errorf("API error: %s", debugMsg.Message)
	}

	return resp, nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
}

// GetTransactionHistory sends a GET request to the /history/transactions/{transactionType} endpoint.
func (c *APIClient) GetTransactionHistory(ctx context.Context, transactionType string, start, end int64) (*http.Response, *TransactionHistorySearchResponse, error) {
	// Use ResolveReference to correctly combine the base URL with the endpoint path.
	localVarPath := c.BasePath.ResolveReference(&url.URL{Path: "/history/transactions/" + url.PathEscape(transactionType)})

	// Add query parameters.
	q := url.Values{}
	q.Add("start", fmt.Sprintf("%d", start))
	q.Add("end", fmt.Sprintf("%d", end))
	localVarPath.RawQuery = q.Encode()

	// Create the request.
	req, err := http.NewRequestWithContext(ctx, "GET", localVarPath.String(), nil)
	if err != nil {
		return nil, nil, fmt.Errorf("error creating request: %w", err)
	}

	// Add Content-Type header.
	req.Header.Add("Content-Type", "application/json")

	// Send the request.
	resp, err := c.HttpClient.Do(req)
	if err != nil {
		return resp, nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	// Handle response based on status code.
	if resp.StatusCode == http.StatusOK {
		var result TransactionHistorySearchResponse
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, nil, fmt.Errorf("error reading response body: %w", err)
		}
		if err = json.Unmarshal(body, &result); err != nil {
			return resp, nil, fmt.Errorf("error unmarshaling response body: %w", err)
		}
		return resp, &result, nil
	} else if resp.StatusCode >= 400 {
		var debugMsg DebugMessageResponse
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp, nil, fmt.Errorf("error reading response body for error: %w", err)
		}
		if err = json.Unmarshal(body, &debugMsg); err != nil {
			return resp, nil, fmt.Errorf("error unmarshaling error response body: %w", err)
		}
		return resp, nil, fmt.Errorf("API error: %s", debugMsg.Message)
	}

	return resp, nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
}
