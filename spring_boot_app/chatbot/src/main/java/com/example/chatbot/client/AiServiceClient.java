package com.example.chatbot.client;

import com.example.chatbot.dto.AiResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import com.example.chatbot.dto.AskRequest;
import reactor.util.retry.Retry;
import java.time.Duration;

@Service
public class AiServiceClient {
    private final WebClient webClient;

    @Value("${ai.service.endpoint:/ask}")
    private String endpoint;

    @Value("${ai.service.client.retry.max}")
    private int maxAttempts;

    @Value("${ai.service.client.retry.delay-ms}")
    private int delay;

    public AiServiceClient(WebClient aiWebClient) {
        this.webClient = aiWebClient;
    }

    public Mono<String> askAi(String question) {
        return webClient.post()
                .uri(endpoint)
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(new AskRequest(question))
                .retrieve()
                .onStatus(HttpStatusCode::isError, response -> response.bodyToMono(String.class).flatMap(body ->
                        Mono.error(new RuntimeException("AI server error: " + body))))
                .bodyToMono(AiResponse.class)
                .map(AiResponse::getAnswer)
                .retryWhen(Retry.backoff(maxAttempts, Duration.ofMillis(delay)).filter(throwable -> throwable instanceof RuntimeException))
                .onErrorResume(e -> {
                    System.err.println("All attempts to connect to the AI have failed: " + e.getMessage());
                    return Mono.just("AI service temporarily unavailable");
                });
    }
}
