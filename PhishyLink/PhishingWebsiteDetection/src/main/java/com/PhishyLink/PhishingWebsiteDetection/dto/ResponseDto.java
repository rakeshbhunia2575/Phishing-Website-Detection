package com.PhishyLink.PhishingWebsiteDetection.dto;

public class ResponseDto {
    private String url;
    private String label;
    private String reason;
    private String notes;
    private String message;

    public ResponseDto() {
    }

    public ResponseDto(String url, String label, String reason, String notes , String message) {
        this.url = url;
        this.label = label;
        this.reason = reason;
        this.notes = notes;
        this.message = message;
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

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
