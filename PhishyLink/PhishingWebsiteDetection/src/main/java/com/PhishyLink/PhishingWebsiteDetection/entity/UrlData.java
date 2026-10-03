package com.PhishyLink.PhishingWebsiteDetection.entity;

import jakarta.persistence.*;
import org.springframework.boot.persistence.autoconfigure.EntityScan;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Entity
public class UrlData {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String url;
    private String label;
    private boolean is_phishing;
    private double confidence;
    private String tire;

    private LocalDateTime dateTime;

    public UrlData() {
    }

    public UrlData(Long id, String url, String label, boolean is_phishing,
                   double confidence, String tire, LocalDateTime dateTime) {
        this.id = id;
        this.url = url;
        this.label = label;
        this.is_phishing = is_phishing;
        this.confidence = confidence;
        this.tire = tire;
        this.dateTime = dateTime;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public String getTire() {
        return tire;
    }

    public void setTire(String tire) {
        this.tire = tire;
    }

    public LocalDateTime getDateTime() {
        return dateTime;
    }

    public void setDateTime(LocalDateTime dateTime) {
        this.dateTime = dateTime;
    }

    public boolean isIs_phishing() {
        return is_phishing;
    }

    public void setIs_phishing(boolean is_phishing) {
        this.is_phishing = is_phishing;
    }
}
