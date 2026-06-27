package com.example.chatbot.controller;
import com.example.chatbot.client.ChatServiceClient;
import com.example.chatbot.client.DocumentServiceClient;
import com.example.chatbot.dto.AskRequest;
import com.example.chatbot.dto.ChatMessage;
import com.example.chatbot.dto.ChatSession;
import com.example.chatbot.dto.UploadedDocument;
import com.example.chatbot.service.AiService;
import jakarta.validation.constraints.Size;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;

import java.util.List;
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

        return aiService.askQuestion(request.getQuestion(), request.getSessionId())
                .doOnSuccess(reply -> log.info("AI response generated in {} ms", System.currentTimeMillis() - start));
    }

    @PostMapping("/api/chat/session")
    public Mono<ChatSession> createSession(@RequestParam(defaultValue = "1") Integer user_id) {
        long start = System.currentTimeMillis();
        return chatServiceClient.initiateSession(user_id)
                .doOnSuccess(reply -> log.info("Chat session created in {} ms", System.currentTimeMillis() - start));
    }

    @GetMapping("/api/chat/session/{sessionId}/history")
    public Mono<List<ChatMessage>> getHistory(@PathVariable UUID sessionId) {
        long start = System.currentTimeMillis();
        return chatServiceClient.fetchChatHistory(sessionId)
                .doOnSuccess(reply -> log.info("History retrieved for session {} in {} ms", sessionId, System.currentTimeMillis() - start));
    }

    @GetMapping("/api/chat/sessions")
    public Mono<List<ChatSession>> getChatSessions() {
        long start = System.currentTimeMillis();
        return chatServiceClient.loadChatList()
                .doOnSuccess(reply -> log.info("Chat sessions showed in {} ms", System.currentTimeMillis() - start));
    }

    @DeleteMapping("/api/chat/session/{session_id}")
    public Mono<ChatSession> deleteChatSession(@PathVariable("session_id") UUID sessionId) {
        long start = System.currentTimeMillis();
        return chatServiceClient.deleteSession(sessionId)
                .doOnSuccess(reply -> log.info("Chat session {} deleted in {} ms", sessionId, System.currentTimeMillis() - start));
    }

    @PutMapping("/api/chat/session/{session_id}")
    public Mono<ChatSession> renameChatSession(@PathVariable("session_id") UUID sessionId, @RequestParam ("title")
    @Size(min=1, max=50, message="The title must be between 1 and 50 characters long") String title) {
        long start = System.currentTimeMillis();
        return chatServiceClient.renameSessionTitle(sessionId, title)
                .doOnSuccess(reply -> log.info("Document {} renamed  in {} ms", sessionId, System.currentTimeMillis() - start));
    }

    @PostMapping("/api/upload")
    public Mono<UploadedDocument> createDocument(@RequestPart("file") MultipartFile file) {
        long start = System.currentTimeMillis();
        return documentServiceClient.proxyUpload(file)
                .flatMap(responseEntity -> {
                    UploadedDocument body = responseEntity.getBody();
                    return body != null ? Mono.just(body) : Mono.empty();
                })
                .doOnSuccess(reply -> log.info("Document created in {} ms", System.currentTimeMillis() - start));
    }

    @GetMapping("/api/documents")
    public Mono<List<UploadedDocument>> getDocuments() {
        long start = System.currentTimeMillis();
        return documentServiceClient.listDocuments()
                .doOnSuccess(reply -> log.info("Documents list retrieved  in {} ms", System.currentTimeMillis() - start));
    }

    @DeleteMapping("/api/documents/{document_id}")
    public Mono<UploadedDocument> deleteDocument(@PathVariable UUID document_id) {
        long start = System.currentTimeMillis();
        return documentServiceClient.deleteDocument(document_id)
                .doOnSuccess(reply -> log.info("Document {} deleted in {} ms", document_id, System.currentTimeMillis() - start));
    }
}
