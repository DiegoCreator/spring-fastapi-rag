package com.example.chatbot.client;

import com.example.chatbot.dto.UploadedDocument;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.IOException;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Service
public class DocumentServiceClient {
    private final WebClient webClient;
    public DocumentServiceClient(WebClient webClient) { this.webClient = webClient; }
    public Mono<ResponseEntity<UploadedDocument>> proxyUpload(@RequestPart("file") MultipartFile file) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();

        try {
            builder.part("file", new InputStreamResource(file.getInputStream())).filename(Objects.requireNonNull(file.getOriginalFilename()));
        } catch (IOException e) {
            return Mono.error(new RuntimeException("Failed to read upload file", e));
        }


        return webClient.post()
                .uri("/upload")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .toEntity(UploadedDocument.class);

    }

    public Mono<List<UploadedDocument>> listDocuments() {
        return webClient.get()
                .uri("/documents")
                .retrieve()
                .bodyToFlux(UploadedDocument.class)
                .collectList();
    }

    public Mono<UploadedDocument> deleteDocument(UUID document_id) {
        return webClient.delete()
                .uri("/documents/{document_id}", document_id)
                .retrieve()
                .bodyToMono(UploadedDocument.class);
    }
}
