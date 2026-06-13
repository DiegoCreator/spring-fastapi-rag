package com.example.chatbot;

import com.example.chatbot.client.AiServiceClient;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import mockwebserver3.MockResponse;
import mockwebserver3.MockWebServer;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;
import java.io.IOException;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class AiServiceClientTests {

    private MockWebServer mockWebServer;
    private AiServiceClient aiServiceClient;

    @BeforeEach
    void setUp() throws IOException {
        mockWebServer = new MockWebServer();
        mockWebServer.start();

        WebClient webClient = WebClient.builder()
                .baseUrl(mockWebServer.url("/").toString()).build();

        aiServiceClient = new AiServiceClient(webClient);

        ReflectionTestUtils.setField(aiServiceClient, "endpoint", "/ask");
        ReflectionTestUtils.setField(aiServiceClient, "maxAttempts", 2);
        ReflectionTestUtils.setField(aiServiceClient, "delay", 100);
    }

    @AfterEach
    void tearDown() throws IOException {
        mockWebServer.shutdown();
    }

    @Test
    void askAi_Success_ReturnsAnswer() {
        mockWebServer.enqueue(new MockResponse.Builder()
                .code(200)
                .setHeader("Content-Type", "application/json")
                .body("{\"answer\":\"Hello World\"}")
                .build());

        Mono<String> result = aiServiceClient.askAi("What is 2+2", UUID.randomUUID());

        StepVerifier.create(result)
                .expectNext("Hello World")
                .verifyComplete();
    }

    @Test
    void askAi_ServerError_RetriesAndReturnsFallback() {
        mockWebServer.enqueue(new MockResponse.Builder().code(500).body("Internal Error").build());
        mockWebServer.enqueue(new MockResponse.Builder().code(500).body("Internal Error").build());
        mockWebServer.enqueue(new MockResponse.Builder().code(500).body("Internal Error").build());

        Mono<String> result = aiServiceClient.askAi("What is 2+2?", UUID.randomUUID());

        StepVerifier.create(result)
                .expectNext("AI service temporarily unavailable")
                .verifyComplete();

        assertEquals(3, mockWebServer.getRequestCount());
    }
}
