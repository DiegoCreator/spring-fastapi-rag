package com.example.chatbot;
import com.example.chatbot.client.ChatServiceClient;
import com.example.chatbot.dto.ChatMessage;
import com.example.chatbot.dto.ChatSession;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;
import tools.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

public class ChatServiceClientTests {
    private MockWebServer mockWebServer;
    private ChatServiceClient chatServiceClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

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
        ChatSession expected_id = ChatSession.builder().session_id(UUID.randomUUID()).build();
        mockWebServer.enqueue(new MockResponse()
                .setBody(objectMapper.writeValueAsString(expected_id))
                .addHeader("Content-Type", "application/json"));

        Mono<ChatSession> result = chatServiceClient.initiateSession(42);

        StepVerifier.create(result)
                .assertNext(session -> assertThat(session.getSession_id()).isEqualTo(expected_id.getSession_id()))
                .verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getMethod()).isEqualTo("POST");
        assertThat(recordedRequest.getPath()).isEqualTo("/chat/session?user_id=42");
    }

    @Test
    void shouldFetchChatHistoryCorrectly() throws InterruptedException {
        UUID sessionId = UUID.randomUUID();
        ChatMessage mockMessage = ChatMessage.builder().content("Hello World").build();
        mockWebServer.enqueue(new MockResponse()
                .setBody(objectMapper.writeValueAsString(List.of(mockMessage)))
                .addHeader("Content-Type", "application/json"));

        Mono<List<ChatMessage>> result = chatServiceClient.fetchChatHistory(sessionId);

        StepVerifier.create(result)
                .assertNext(message -> {
                    assertThat(message).isNotEmpty();
                    assertThat(message.getFirst().getContent()).isEqualTo("Hello World");
                })
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
        ChatSession expected_id = ChatSession.builder().session_id(UUID.randomUUID()).build();

        mockWebServer.enqueue(new MockResponse()
                .setBody(objectMapper.writeValueAsString(expected_id))
                .addHeader("Content-Type", "application/json"));
        Mono<List<ChatSession>> result = chatServiceClient.loadChatList();

        StepVerifier.create(result)
                .assertNext(sessions -> assertThat(sessions.getFirst().getSession_id()).isEqualTo(expected_id.getSession_id()))
                .verifyComplete();

        RecordedRequest recordedRequest = mockWebServer.takeRequest();
        assertThat(recordedRequest.getMethod()).isEqualTo("GET");
        assertThat(recordedRequest.getPath()).isEqualTo("/chat/sessions");

    }

    @Test
    void shouldReturnErrorWhenLoadChatListEndpointReturns404() {

        mockWebServer.enqueue(
                new MockResponse().setResponseCode(404)
        );

        StepVerifier.create(chatServiceClient.loadChatList())
                .expectError()
                .verify();
    }
}
