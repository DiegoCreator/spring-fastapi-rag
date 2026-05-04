package com.example.chatbot.service;

import com.example.chatbot.client.AiServiceClient;
import org.springframework.stereotype.Service;

@Service
public class AiService {
    private final AiServiceClient aiServiceClient;

    public AiService(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    public String askQuestion(String question) {

        if (question == null || question.isBlank()) {
            return "Question cannot be empty";
        }

        String enrichedQuestion = "Answer briefly: " + question;

        String response = aiServiceClient.askAi(enrichedQuestion);

        return response.trim();
    }
}
