package com.example.chatbot.controller;

import com.example.chatbot.client.AiServiceClient;
import com.example.chatbot.dto.AskRequest;
import com.example.chatbot.service.AiService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;

@Slf4j
@RestController
public class AiController {

    private final AiService aiService;

    public AiController(AiService aiService, AiServiceClient aiServiceClient) {
        this.aiService = aiService;
    }

    @PostMapping("/api/ask")
    public Mono<String> ask(@RequestBody AskRequest request) {
        long start = System.currentTimeMillis();
        return aiService.askQuestion(request.getQuestion()) // Assuming this returns Mono<String>
                .doOnSuccess(reply -> log.info("AI response generated in {} ms", System.currentTimeMillis() - start));
    }
}
