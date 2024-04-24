FROM gradle:7.1.0-jdk11 AS build
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src
RUN gradle shadowjar --no-daemon 

FROM eclipse-temurin:11
RUN mkdir /app
COPY --from=build /home/gradle/src/build/libs/*.jar /app/hbase-client.jar
WORKDIR /app
CMD ["java", "-jar", "/app/hbase-client.jar"]
