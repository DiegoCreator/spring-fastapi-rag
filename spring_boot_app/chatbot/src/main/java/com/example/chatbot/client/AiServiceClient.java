package com.example.chatbot.client;

import com.example.chatbot.dto.AiResponse;
import org.springframework.http.MediaType;
import org.springframework.retry.annotation.Retryable;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Recover;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Map;

@Service
public class AiServiceClient {
    private final WebClient webClient;

    public AiServiceClient(WebClient aiWebClient) {
        this.webClient = aiWebClient;
    }

    @Retryable(
            value = {  RuntimeException.class },
            maxAttempts = 3,
            backoff = @Backoff(delay = 1000, multiplier = 2)
    )

    public String askAi(String question) {
        return webClient.post()
                .uri("/ask")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(Map.of("question", question))
                .retrieve()
                .bodyToMono(AiResponse.class)
                .map(AiResponse::getAnswer)
                .block();
    }

    @Recover
    public String recover(RuntimeException e, String question) {
        return "AI service temporarily unavailable";
    }
}
