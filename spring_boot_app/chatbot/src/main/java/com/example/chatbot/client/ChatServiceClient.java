package com.example.chatbot.client;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.UUID;

@Service
public class ChatServiceClient {
    private final WebClient webClient;
    public ChatServiceClient(WebClient aiWebClient) {
        this.webClient = aiWebClient;
    }

    public Mono<String> initiateSession(Integer userId) {
        return webClient.post()
                .uri(uriBuilder -> uriBuilder
                        .path("/chat/session")
                        .queryParam("user_id", userId)
                        .build())
                .retrieve()
                .bodyToMono(String.class);
    }

    public Mono<String> fetchChatHistory(UUID sessionId) {
        return webClient.get()
                .uri("/chat/session/{sessionId}/history", sessionId)
                .retrieve()
                .bodyToMono(String.class);
    }

    public Mono<String> loadChatList() {
        return webClient.get()
                .uri("/chat/sessions")
                .retrieve()
                .bodyToMono(String.class);
    }
}
