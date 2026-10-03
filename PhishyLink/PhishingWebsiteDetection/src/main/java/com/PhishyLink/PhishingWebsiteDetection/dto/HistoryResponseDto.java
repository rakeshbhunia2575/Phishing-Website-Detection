package com.PhishyLink.PhishingWebsiteDetection.dto;

public class HistoryResponseDto {
    private String url;
    private String label;
    private double confidence;

    public HistoryResponseDto() {
    }

    public HistoryResponseDto(String url, String label, double confidence) {
        this.url = url;
        this.label = label;
        this.confidence = confidence;
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
}
