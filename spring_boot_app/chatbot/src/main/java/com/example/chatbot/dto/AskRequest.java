package com.example.chatbot.dto;

import lombok.Getter;

@Getter
public class AskRequest {
    private String question;

    public AskRequest(String question) {
        this.question = question;
    }
}
