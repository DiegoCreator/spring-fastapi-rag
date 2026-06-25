package com.example.chatbot;

import com.example.chatbot.client.DocumentServiceClient;
import com.example.chatbot.dto.UploadedDocument;
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
import java.util.Objects;
import java.util.UUID;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;

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

        String mockJsonArray = """
              {
              "id": "%s", "filename": "test.txt"
              }
            """.formatted(UUID.randomUUID());

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(201)
                .setHeader("Content-Type", "application/json")
                .setBody(mockJsonArray));

        StepVerifier.create(documentServiceClient.proxyUpload(mockFile))
                .assertNext(response -> {
                    assertThat(response.getStatusCode().value()).isEqualTo(201);

                    UploadedDocument body = response.getBody();

                    assertThat(body).isNotNull();
                    assertThat(Objects.requireNonNull(body).getFilename()).isEqualTo("test.txt");
                    assertThat(body.getId()).isNotNull();
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

        String mockJsonArray = """
            [
              {"id": "%s", "filename": "doc1"},
              {"id": "%s", "filename": "doc2"}
            ]
            """.formatted(UUID.randomUUID(), UUID.randomUUID());

        mockWebServer.enqueue(new MockResponse()
                .setResponseCode(200)
                .setHeader("Content-Type", "application/json")
                .setBody(mockJsonArray));

        StepVerifier.create(documentServiceClient.listDocuments()).assertNext(docs -> {
             assertThat(docs.getFirst().getFilename()).isEqualTo("doc1");
             assertThat(docs.get(1).getFilename()).isEqualTo("doc2");
        }).verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getPath()).isEqualTo("/documents");
        assertThat(recordedRequest.getMethod()).isEqualTo("GET");
    }

    @Test
    void shouldDeleteDocumentCorrectly() throws InterruptedException {
        UUID docId = UUID.randomUUID();

        String mockJsonArray = """
              {
              "id": "%s", "filename": "Deleted"
              }
            """.formatted(docId);

        mockWebServer.enqueue(new MockResponse().setResponseCode(200).setHeader("Content-Type", "application/json").setBody(mockJsonArray));

        StepVerifier.create(documentServiceClient.deleteDocument(docId))
                .assertNext(deletedDoc -> assertThat(deletedDoc.getId()).isEqualTo(docId))
                .verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getMethod()).isEqualTo("DELETE");
        assertThat(recordedRequest.getPath()).isEqualTo("/documents/" + docId);
    }

}
