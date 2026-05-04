FROM eclipse-temurin:21-jre-jammy

WORKDIR /app

COPY build/libs/*.jar app.jar

COPY src/main/resources/application.properties /app/application.properties

ENTRYPOINT ["java","-jar","app.jar", "--spring.config.location=file:/app/application.properties"]