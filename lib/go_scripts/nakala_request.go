package main

import "C"
import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"sync/atomic"
	"time"
	"unsafe"
)

const (
	maxRetries = 10   // Number of retries in case of failure
	maxWorkers = 20  // Number of concurrent uploads (go routines)
)

func createFileCur(imagePath string) (map[string]io.Reader, error) {
	file, err := os.Open(imagePath)
	if err != nil {
		return nil, err
	}
	return map[string]io.Reader{filepath.Base(imagePath): file}, nil
}

func post(endpoint, apiKey string, data map[string]string, files map[string]io.Reader) (string, error) {
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	for key, r := range files {
		part, err := writer.CreateFormFile("file", key)
		if err != nil {
			return "", err
		}
		_, err = io.Copy(part, r)
		if err != nil {
			return "", err
		}
	}

	for key, val := range data {
		_ = writer.WriteField(key, val)
	}

	err := writer.Close()
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", endpoint, body)
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("X-API-KEY", apiKey)
	req.Header.Set("accept", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(respBody), nil
}

func addFile(url, apiKey, filePath string) map[string]string {
	var response string
	var err error

	for attempt := 1; attempt <= maxRetries; attempt++ {
		fileMap, err := createFileCur(filePath)
		if err != nil {
			return map[string]string{"name": filePath, "sha1": ""}
		}
		response, err = post(url, apiKey, map[string]string{}, fileMap)
		if err == nil {
			break
		}
		time.Sleep(time.Duration(attempt) * 2 * time.Second) // exponential backoff
	}

	if err != nil {
		return map[string]string{"name": filePath, "sha1": ""}
	}
	var result map[string]string
	json.Unmarshal([]byte(response), &result)
	result["name"] = filepath.Base(filePath)
	return result
}

//export UploadFiles
func UploadFiles(url, apiKey *C.char, filePaths **C.char, length C.int) *C.char {
	goURL := C.GoString(url)
	goAPIKey := C.GoString(apiKey)
	goFilePaths := make([]string, length)
	ptr := uintptr(unsafe.Pointer(filePaths))
	for i := 0; i < int(length); i++ {
		goFilePaths[i] = C.GoString(*(**C.char)(unsafe.Pointer(ptr)))
		ptr += unsafe.Sizeof(ptr)
	}

	var wg sync.WaitGroup
	var processedCount int32
	totalFiles := len(goFilePaths)
	responses := make([]map[string]string, totalFiles)

	sem := make(chan struct{}, maxWorkers) // semaphore to limit the number of concurrent uploads

	for i, filePath := range goFilePaths {
		wg.Add(1)
		go func(i int, filePath string) {
			defer wg.Done()
			sem <- struct{}{} // get a token
			defer func() { <-sem }() // release the token

			responses[i] = addFile(goURL, goAPIKey, filePath)
			atomic.AddInt32(&processedCount, 1)
			fmt.Printf("\rNakala upload files in progress...: %d/%d", processedCount, totalFiles)
		}(i, filePath)
	}
	wg.Wait()
	fmt.Println()

	jsonResponses, _ := json.Marshal(responses)
	return C.CString(string(jsonResponses))
}

func main() {}
