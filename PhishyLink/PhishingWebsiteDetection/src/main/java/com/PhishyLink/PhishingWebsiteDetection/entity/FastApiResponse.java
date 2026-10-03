package com.PhishyLink.PhishingWebsiteDetection.entity;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

public class FastApiResponse {
    private String url;
    private String label;
    private @JsonProperty("is_phishing") boolean isPhishing;
    private double confidence;
    private String tier;
    private List<String> reasons;
    private List<String> notes;
    private Map<String, Integer> features;

    public FastApiResponse(String url, String label, boolean isPhishing,
                           double confidence, String tier, List<String> reasons,
                           List<String> notes, Map<String, Integer> features) {
        this.url = url;
        this.label = label;
        this.isPhishing = isPhishing;
        this.confidence = confidence;
        this.tier = tier;
        this.reasons = reasons;
        this.notes = notes;
        this.features = features;
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

    public boolean isPhishing() {
        return isPhishing;
    }

    public void setPhishing(boolean phishing) {
        isPhishing = phishing;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public String getTier() {
        return tier;
    }

    public void setTier(String tier) {
        this.tier = tier;
    }

    public List<String> getReasons() {
        return reasons;
    }

    public void setReasons(List<String> reasons) {
        this.reasons = reasons;
    }

    public List<String> getNotes() {
        return notes;
    }

    public void setNotes(List<String> notes) {
        this.notes = notes;
    }

    public Map<String, Integer> getFeatures() {
        return features;
    }

    public void setFeatures(Map<String, Integer> features) {
        this.features = features;
    }
}
