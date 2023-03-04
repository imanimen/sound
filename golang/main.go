package golang

import (
	_"os"
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

const openaiApiKey = "YOUR_API_KEY"

func main() {
	http.HandleFunc("/transcribe", transcribeHandler)
	fmt.Println("Server running on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}

func transcribeHandler(w http.ResponseWriter, r *http.Request) {
	// Read the audio file from the request
	file, _, err := r.FormFile("audio")
	if err != nil {
		http.Error(w, "Failed to read audio file from request", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Read the audio file contents
	audioContent, err := ioutil.ReadAll(file)
	if err != nil {
		http.Error(w, "Failed to read audio file contents", http.StatusInternalServerError)
		return
	}

	// Encode the audio file contents in base64 format
	audioBase64 := base64.StdEncoding.EncodeToString(audioContent)

	// Create the request to the OpenAI API
	requestBody := map[string]interface{}{
		"prompt": fmt.Sprintf("Transcribe the following speech:\n%s", audioBase64),
		"temperature": 0.5,
		"max_tokens": 2048,
		"n": 1,
	}
	requestBytes, err := json.Marshal(requestBody)
	if err != nil {
		http.Error(w, "Failed to create request to OpenAI API", http.StatusInternalServerError)
		return
	}
	requestBuffer := bytes.NewBuffer(requestBytes)

	// Send the request to the OpenAI API
	apiUrl := "https://api.openai.com/v1/completions"
	req, err := http.NewRequest("POST", apiUrl, requestBuffer)
	if err != nil {
		http.Error(w, "Failed to create request to OpenAI API", http.StatusInternalServerError)
		return
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", openaiApiKey))
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Failed to send request to OpenAI API", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from the OpenAI API
	responseBody, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Failed to read response from OpenAI API", http.StatusInternalServerError)
		return
	}

	// Extract the transcript from the response
	type Choice struct {
		Text string `json:"text"`
	}
	type Response struct {
		Choices []Choice `json:"choices"`
	}
	var response Response
	err = json.Unmarshal(responseBody, &response)
	if err != nil {
		http.Error(w, "Failed to extract transcript from OpenAI API response", http.StatusInternalServerError)
		return
	}
	transcript := response.Choices[0].Text

	// Return the transcript
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"transcript": transcript,
	})
}
