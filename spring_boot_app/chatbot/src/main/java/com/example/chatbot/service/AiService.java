package com.example.chatbot.service;
import lombok.extern.slf4j.Slf4j;
import com.example.chatbot.client.AiServiceClient;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

import java.util.UUID;

@Slf4j
@Service
public class AiService {
    private final AiServiceClient aiServiceClient;

    public AiService(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    public Mono<String> askQuestion(String question, UUID sessionId) {

        if (question == null || question.isBlank()) {
            log.warn("Attempted to ask AI with empty question");
            return Mono.error(new IllegalArgumentException("Question cannot be null or empty"));
        }

        return aiServiceClient.askAi(question, sessionId)
                .map(String::valueOf)
                .map(String::trim)
                .doOnSubscribe(subscription -> log.debug("Sending request to AI service"))
                .doOnNext(response -> {
                    if (response.isBlank()) {
                        log.warn("AI service returned empty response");
                    }
                })
                .doOnError(error -> log.error("Failed to get response from AI service", error));

    }
}
