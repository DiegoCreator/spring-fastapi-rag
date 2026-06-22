package com.example.chatbot;

import com.example.chatbot.client.DocumentServiceClient;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.test.StepVerifier;

import java.io.IOException;
import java.util.UUID;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class DocumentServiceClientTests {
    private MockWebServer mockWebServer;
    private DocumentServiceClient documentServiceClient;

    @BeforeEach
    void setUp() throws IOException {
        this.mockWebServer = new MockWebServer();
        this.mockWebServer.start();

        WebClient webClient = WebClient.builder()
                .baseUrl(mockWebServer.url("/").toString())
                .build();

        this.documentServiceClient = new DocumentServiceClient(webClient);
    }

    @AfterEach
    void tearDown() throws IOException {
        this.mockWebServer.shutdown();
    }

    @Test
    void shouldProxyUploadCorrectly() throws InterruptedException {
        MockMultipartFile mockFile = new MockMultipartFile("file", "test.txt", MediaType.TEXT_PLAIN_VALUE, "hello world".getBytes());

        mockWebServer.enqueue(new MockResponse().setResponseCode(201).setBody("Uploaded"));

        StepVerifier.create(documentServiceClient.proxyUpload(mockFile))
                .assertNext(response -> {
                    assertThat(response.getStatusCode().value()).isEqualTo(201);
                    assertThat(response.getBody()).isEqualTo("Uploaded");
                }).verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getHeader("Content-Type")).contains("multipart/form-data");
        assertThat(recordedRequest.getPath()).isEqualTo("/upload");
        assertThat(recordedRequest.getMethod()).isEqualTo("POST");
    }

    @Test
    void proxyUpload_ioException_shouldReturnMonoError() throws IOException {
        MultipartFile brokenFile = org.mockito.Mockito.mock(MultipartFile.class);
        org.mockito.Mockito.when(brokenFile.getInputStream()).thenThrow(new IOException("Disk failure"));

        StepVerifier.create(documentServiceClient.proxyUpload(brokenFile))
                .expectErrorMatches(throwable -> throwable instanceof RuntimeException && throwable.getMessage().equals("Failed to read upload file"))
                .verify();
    }

    @Test
    void shouldListDocumentCorrectly() throws InterruptedException {
        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "application/json")
                .setBody("[\"doc1\", \"doc2\"]"));

        StepVerifier.create(documentServiceClient.listDocuments()).expectNext("[\"doc1\", \"doc2\"]").verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getPath()).isEqualTo("/documents");
        assertThat(recordedRequest.getMethod()).isEqualTo("GET");
    }

    @Test
    void shouldDeleteDocumentCorrectly() throws InterruptedException {
        UUID docId = UUID.randomUUID();
        mockWebServer.enqueue(new MockResponse().setResponseCode(200).setBody("Deleted"));

        StepVerifier.create(documentServiceClient.deleteDocument(docId))
                .expectNext("Deleted")
                .verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getMethod()).isEqualTo("DELETE");
        assertThat(recordedRequest.getPath()).isEqualTo("/documents/" + docId);
    }

}
