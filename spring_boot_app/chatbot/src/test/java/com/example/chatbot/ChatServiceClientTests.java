package com.example.chatbot;
import com.example.chatbot.client.ChatServiceClient;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import java.io.IOException;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

public class ChatServiceClientTests {
    private MockWebServer mockWebServer;
    private ChatServiceClient chatServiceClient;

    @BeforeEach
    void setUp() throws IOException {
        this.mockWebServer = new MockWebServer();
        this.mockWebServer.start();

        WebClient webClient = WebClient.builder()
                .baseUrl(mockWebServer.url("/").toString())
                .build();

        this.chatServiceClient = new ChatServiceClient(webClient);
    }

    @AfterEach
    void tearDown() throws IOException {
        this.mockWebServer.shutdown();
    }

    @Test
    void shouldInitiateSessionCorrectly() throws InterruptedException {
        mockWebServer.enqueue(new MockResponse()
                .setBody("mocked-session-id-123")
                .addHeader("Content-Type", "application/json"));

        Mono<String> result = chatServiceClient.initiateSession(42);

        StepVerifier.create(result)
                .expectNext("mocked-session-id-123")
                .verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getMethod()).isEqualTo("POST");
        assertThat(recordedRequest.getPath()).isEqualTo("/chat/session?user_id=42");
    }

    @Test
    void shouldFetchChatHistoryCorrectly() throws InterruptedException {
        UUID sessionId = UUID.randomUUID();
        mockWebServer.enqueue(new MockResponse()
                .setBody("mocked-session-id-123")
                .addHeader("Content-Type", "application/json"));

        Mono<String> result = chatServiceClient.fetchChatHistory(sessionId);

        StepVerifier.create(result)
                .expectNext("mocked-session-id-123")
                .verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getMethod()).isEqualTo("GET");
        assertThat(recordedRequest.getPath()).isEqualTo("/chat/session/" + sessionId + "/history");
    }

    @Test
    void shouldReturnErrorWhenHistoryEndpointReturns404() {
        UUID sessionId = UUID.randomUUID();

        mockWebServer.enqueue(
                new MockResponse().setResponseCode(404)
        );

        StepVerifier.create(chatServiceClient.fetchChatHistory(sessionId))
                .expectError()
                .verify();
    }

    @Test
    void shouldLoadChatListCorrectly() throws InterruptedException {
        mockWebServer.enqueue(new MockResponse()
                .setBody("mocked-session-id-123")
                .addHeader("Content-Type", "application/json"));
        Mono<String> result = chatServiceClient.loadChatList();

        StepVerifier.create(result)
                .expectNext("mocked-session-id-123")
                .verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getMethod()).isEqualTo("GET");
        assertThat(recordedRequest.getPath()).isEqualTo("/chat/sessions");

    }

    @Test
    void shouldReturnErrorWhenLoadChatListEndpointReturns404() {
        UUID sessionId = UUID.randomUUID();

        mockWebServer.enqueue(
                new MockResponse().setResponseCode(404)
        );

        StepVerifier.create(chatServiceClient.loadChatList())
                .expectError()
                .verify();
    }
}
