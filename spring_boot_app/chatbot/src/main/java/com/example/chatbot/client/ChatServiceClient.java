package com.example.chatbot.client;

import com.example.chatbot.dto.ChatMessage;
import com.example.chatbot.dto.ChatSession;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.UUID;

@Service
public class ChatServiceClient {
    private final WebClient webClient;
    public ChatServiceClient(WebClient aiWebClient) {
        this.webClient = aiWebClient;
    }

    public Mono<ChatSession> initiateSession(Integer user_id) {
        return webClient.post()
                .uri(uriBuilder -> uriBuilder
                        .path("/chat/session")
                        .queryParam("user_id", user_id)
                        .build())
                .retrieve()
                .bodyToMono(ChatSession.class);
    }

    public Mono<List<ChatMessage>> fetchChatHistory(UUID sessionId) {
        return webClient.get()
                .uri("/chat/session/{sessionId}/history", sessionId)
                .retrieve()
                .bodyToFlux(ChatMessage.class)
                .collectList();
    }

    public Mono<List<ChatSession>> loadChatList() {
        return webClient.get()
                .uri("/chat/sessions")
                .retrieve()
                .bodyToFlux(ChatSession.class)
                .collectList();
    }

    public Mono<ChatSession> deleteSession(UUID sessionId) {
        return webClient.delete()
                .uri("/chat/session/{session_id}", sessionId)
                .retrieve()
                .bodyToMono(ChatSession.class);
    }

    public Mono<ChatSession> renameSessionTitle(UUID sessionId, String title) {
        return webClient.put()
                .uri(uriBuilder -> uriBuilder
                        .path("/chat/session/{session_id}")
                        .queryParam("title", title)
                        .build(sessionId))
                .retrieve()
                .bodyToMono(ChatSession.class);
    }
}
