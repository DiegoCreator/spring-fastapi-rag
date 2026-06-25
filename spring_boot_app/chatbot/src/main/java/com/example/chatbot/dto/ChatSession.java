package com.example.chatbot.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.UUID;
@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Data
public class ChatSession {
    private UUID session_id;
    private Integer user_id;
    private String title;
    private LocalDateTime created_at;
}
