package com.PhishyLink.PhishingWebsiteDetection.exceptions;

import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(InvalidUrlException.class)
    public ResponseEntity<String> badUrl(InvalidUrlException e) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(e.getMessage());
    }

    @ExceptionHandler(OutOfServiceException.class)
    public ResponseEntity<String> unavailable(OutOfServiceException e) {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> any(Exception e) {
        e.printStackTrace();
        return ResponseEntity.status(500)
                .body(e.getClass().getName() + ": " + e.getMessage());
    }
}
