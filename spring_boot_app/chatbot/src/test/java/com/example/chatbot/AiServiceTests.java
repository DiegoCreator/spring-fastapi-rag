package com.example.chatbot;

import com.example.chatbot.client.AiServiceClient;
import com.example.chatbot.service.AiService;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;
import java.util.UUID;

@Slf4j
@ExtendWith(MockitoExtension.class)
class AiServiceTests {

    @Mock
    private AiServiceClient aiServiceClient;

    @InjectMocks
    private AiService aiService;

    @Test
    void askQuestion_withValidInput_returnsTrimmedResponse() {
        // Arrange
        UUID sessionId = UUID.randomUUID();
        String question = "What is Java?";
        String expectedPrompt = "Answer briefly: What is Java?";

        Mockito.when(aiServiceClient.askAi(expectedPrompt, sessionId))
                .thenReturn(Mono.just("   It is a language.   "));

        Mono<String> result = aiService.askQuestion(question, sessionId);

        StepVerifier.create(result)
                .expectNext("It is a language.")
                .verifyComplete();

        Mockito.verify(aiServiceClient, Mockito.times(1)).askAi(expectedPrompt, sessionId);
    }

    @Test
    void askQuestion_whenQuestionIsNull_shouldThrowIllegalArgumentException() {
        UUID sessionId = UUID.randomUUID();
        Mono<String> result = aiService.askQuestion(null, sessionId);

        StepVerifier.create(result)
                .expectErrorMatches(ex ->
                        ex instanceof IllegalArgumentException && ex.getMessage().equals("Question cannot be null or empty"))
                .verify();

        Mockito.verifyNoInteractions(aiServiceClient);
    }

    @Test
    void askQuestion_whenQuestionIsBlank_shouldThrowIllegalArgumentException() {
        UUID sessionId = UUID.randomUUID();
        Mono<String> result = aiService.askQuestion(" ", sessionId);

        StepVerifier.create(result)
                .expectErrorMatches(ex ->
                        ex instanceof IllegalArgumentException && ex.getMessage().equals("Question cannot be null or empty"))
                .verify();

        Mockito.verifyNoInteractions(aiServiceClient);
    }

    @Test
    void askQuestion_whenAiReturnsEmptyResponse_shouldCompleteEmpty() {
        UUID sessionId = UUID.randomUUID();
        Mockito.when(aiServiceClient.askAi(Mockito.anyString(), Mockito.eq(sessionId)))
                .thenReturn(Mono.empty());

        Mono<String> result = aiService.askQuestion("What is Java?", sessionId);

        StepVerifier.create(result)
                .verifyComplete();
    }

    @Test
    void askQuestion_clientThrowsError_propagatesError() {
        UUID sessionId = UUID.randomUUID();
        String question = "What is Java?";
        String expectedPrompt = "Answer briefly: What is Java?";
        RuntimeException simulatedError = new RuntimeException("Connection timed out");

        Mockito.when(aiServiceClient.askAi(expectedPrompt, sessionId))
                .thenReturn(Mono.error(simulatedError));

        Mono<String> result = aiService.askQuestion(question, sessionId);

        StepVerifier.create(result)
                .expectErrorMatches(ex -> ex instanceof  RuntimeException && ex.getMessage().equals("Connection timed out")).verify();
    }

    @Test
    void askQuestion_clientReturnsBlankString_triggersBlankCheck() {
        UUID sessionId = UUID.randomUUID();
        String question = "What is Java?";

        Mockito.when(aiServiceClient.askAi(Mockito.anyString(), Mockito.eq(sessionId)))
                .thenReturn(Mono.just("   "));

        Mono<String> result = aiService.askQuestion(question, sessionId);

        StepVerifier.create(result)
                .expectNext("")
                .verifyComplete();
    }
}
