package com.example.chatbot.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Data
public class ChatMessage {
    private UUID session_id;
    private UUID message_id;
    private String role;
    private String content;
    private List<Double> embedding;
    private LocalDateTime created_at;
}
