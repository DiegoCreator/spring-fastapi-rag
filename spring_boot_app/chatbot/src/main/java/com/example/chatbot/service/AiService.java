package com.example.chatbot.service;

import com.example.chatbot.client.AiServiceClient;
import org.springframework.stereotype.Service;

@Service
public class AiService {
    private final AiServiceClient aiServiceClient;

    private static final String PROMPT_PREFIX = "Answer briefly: ";

    public AiService(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    public String askQuestion(String question) {

        if (question == null || question.isBlank()) {
            throw new IllegalArgumentException("Question cannot be null or empty");
        }

        String enrichedQuestion = PROMPT_PREFIX + question;

        Object rawResponse = aiServiceClient.askAi(enrichedQuestion);
        String response = (rawResponse != null) ? String.valueOf(rawResponse) : "";

        return response.trim();
    }
}
