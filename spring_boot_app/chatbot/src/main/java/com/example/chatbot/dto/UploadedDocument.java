package com.example.chatbot.dto;

import lombok.*;

import java.util.UUID;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Data
public class UploadedDocument {
    private UUID id;
    private String filename;
    private String path;
}
