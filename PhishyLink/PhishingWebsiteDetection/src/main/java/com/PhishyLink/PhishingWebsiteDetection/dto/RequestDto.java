package com.PhishyLink.PhishingWebsiteDetection.dto;

public class RequestDto {
   private String urlReq;

   public RequestDto(){}
    public RequestDto(String urlReq) {
        this.urlReq = urlReq;
    }

    public String getUrlReq() {
        return urlReq;
    }

    public void setUrlReq(String urlReq) {
        this.urlReq = urlReq;
    }
}
