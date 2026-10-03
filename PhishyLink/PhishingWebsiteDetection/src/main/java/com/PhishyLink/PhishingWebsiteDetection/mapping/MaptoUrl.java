package com.PhishyLink.PhishingWebsiteDetection.mapping;

import com.PhishyLink.PhishingWebsiteDetection.entity.FastApiResponse;
import com.PhishyLink.PhishingWebsiteDetection.entity.UrlData;

import java.time.LocalDateTime;

public class MaptoUrl {
    public static UrlData maptoUrl(FastApiResponse fastApiResponse){
       UrlData urlData = new UrlData();

       urlData.setUrl(fastApiResponse.getUrl());
       urlData.setLabel(fastApiResponse.getLabel());
       urlData.setConfidence(fastApiResponse.getConfidence());
       urlData.setTire(fastApiResponse.getTier());
       urlData.setDateTime(LocalDateTime.now());
       urlData.setIs_phishing(fastApiResponse.isPhishing());


       return urlData;
    }
}
