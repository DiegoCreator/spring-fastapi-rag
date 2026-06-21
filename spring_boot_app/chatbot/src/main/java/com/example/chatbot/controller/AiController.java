package com.example.chatbot.controller;
import com.example.chatbot.client.ChatServiceClient;
import com.example.chatbot.client.DocumentServiceClient;
import com.example.chatbot.dto.AskRequest;
import com.example.chatbot.service.AiService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;
import java.util.UUID;

@Slf4j
@RestController
public class AiController {
    private final AiService aiService;
    private final ChatServiceClient chatServiceClient;
    private final DocumentServiceClient documentServiceClient;

    public AiController(AiService aiService, ChatServiceClient chatServiceClient, DocumentServiceClient documentServiceClient) {
        this.aiService = aiService;
        this.chatServiceClient = chatServiceClient;
        this.documentServiceClient = documentServiceClient;
    }

    @PostMapping("/api/ask")
    public Mono<String> ask(@RequestBody AskRequest request) {
        long start = System.currentTimeMillis();

        return aiService.askQuestion(request.getQuestion(), request.getSessionId()) // Assuming this returns Mono<String>
                .doOnSuccess(reply -> log.info("AI response generated in {} ms", System.currentTimeMillis() - start));
    }

    @PostMapping("/api/chat/session")
    public Mono<String> createSession(@RequestParam(defaultValue = "1") Integer user_id) {
        long start = System.currentTimeMillis();
        return chatServiceClient.initiateSession(user_id)
                .doOnSuccess(reply -> log.info("Chat session created in {} ms", System.currentTimeMillis() - start));
    }

    @GetMapping("/api/chat/session/{sessionId}/history")
    public Mono<String> getHistory(@PathVariable UUID sessionId) {
        long start = System.currentTimeMillis();
        return chatServiceClient.fetchChatHistory(sessionId)
                .doOnSuccess(reply -> log.info("History retrieved for session {} in {} ms", sessionId, System.currentTimeMillis() - start));
    }

    @GetMapping("/api/chat/sessions")
    public Mono<String> getChatSessions() {
        long start = System.currentTimeMillis();
        return chatServiceClient.loadChatList()
                .doOnSuccess(reply -> log.info("Chat sessions showed in {} ms", System.currentTimeMillis() - start));
    }

    @PostMapping("/api/upload")
    public Mono<String> createDocument(@RequestPart("file") MultipartFile file) {
        long start = System.currentTimeMillis();
        return documentServiceClient.proxyUpload(file)
                .map(responseEntity -> {
                    String body = responseEntity.getBody();
                    return body != null ? body : "";
                })
                .doOnSuccess(reply -> log.info("Document created in {} ms", System.currentTimeMillis() - start));
    }

    @GetMapping("/api/documents")
    public Mono<String> getDocuments() {
        long start = System.currentTimeMillis();
        return documentServiceClient.listDocuments()
                .doOnSuccess(reply -> log.info("Documents list retrieved  in {} ms", System.currentTimeMillis() - start));
    }

    @DeleteMapping("/api/chat/session/{session_id}")
    public Mono<String> deleteChatSession(@PathVariable("session_id") UUID sessionId) {
        long start = System.currentTimeMillis();
        return chatServiceClient.deleteSession(sessionId)
                .doOnSuccess(reply -> log.info("Chat session {} deleted in {} ms", sessionId, System.currentTimeMillis() - start));
    }

    @DeleteMapping("/api/documents/{document_id}")
    public Mono<String> deleteDocument(@PathVariable UUID document_id) {
        long start = System.currentTimeMillis();
        return documentServiceClient.deleteDocument(document_id)
                .doOnSuccess(reply -> log.info("Document {} deleted in {} ms", document_id, System.currentTimeMillis() - start));
    }

}
