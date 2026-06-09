package com.example.chatbot.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;

import java.util.UUID;

@Getter
public class AskRequest {
    private String question;

    @JsonProperty("session_id")
    private UUID sessionId;

    public AskRequest(String question, UUID sessionId) {
        this.question = question;
        this.sessionId = sessionId;
    }
}
