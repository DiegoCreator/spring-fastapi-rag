package com.example.chatbot.service;
import lombok.extern.slf4j.Slf4j;
import com.example.chatbot.client.AiServiceClient;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class AiService {
    private final AiServiceClient aiServiceClient;

    private static final String PROMPT_PREFIX = "Answer briefly: ";

    public AiService(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    public String askQuestion(String question) {

        if (question == null || question.isBlank()) {
            log.warn("Attempted to ask AI with empty question");
            throw new IllegalArgumentException("Question cannot be null or empty");
        }

        String enrichedQuestion = PROMPT_PREFIX + question;

        try {
            log.debug("Sending request to AI service");

            Object rawResponse = aiServiceClient.askAi(enrichedQuestion);
            String response = (rawResponse != null) ? String.valueOf(rawResponse) : "";

            if (response.isBlank()) {
                log.warn("AI service returned empty response");
            }

            return response.trim();
        } catch (Exception e) {
            log.error("Failed to get response from AI service");
            throw e;
        }
    }
}
