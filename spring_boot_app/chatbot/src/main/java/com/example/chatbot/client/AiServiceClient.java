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
import lombok.extern.slf4j.Slf4j;

@Slf4j
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

        log.debug("Sending AI request endpoint={}", endpoint);

        return webClient.post()
                .uri(endpoint)
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(new AskRequest(question))
                .retrieve()
                .onStatus(HttpStatusCode::isError, response -> response.bodyToMono(String.class).flatMap(body -> {
                        log.warn("AI service error status={} body{}", response.statusCode(), body);
                        return Mono.error(new RuntimeException("AI server error"));
                }))
                .bodyToMono(AiResponse.class)
                .map(AiResponse::getAnswer)
                .retryWhen(Retry.backoff(maxAttempts, Duration.ofMillis(delay)).filter(throwable -> throwable instanceof RuntimeException)
                        .doAfterRetry(retrySignal ->
                                log.warn("Retry AI request attempt={}", retrySignal.totalRetries() + 1))
                )
                .onErrorResume(e -> {
                    log.error("AI request failed after retries", e);

                    return Mono.just("AI service temporarily unavailable");
                });
    }
}
