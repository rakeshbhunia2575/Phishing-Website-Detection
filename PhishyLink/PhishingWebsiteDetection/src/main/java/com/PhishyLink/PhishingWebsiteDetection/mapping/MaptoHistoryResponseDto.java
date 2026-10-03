package com.PhishyLink.PhishingWebsiteDetection.mapping;

import com.PhishyLink.PhishingWebsiteDetection.dto.HistoryResponseDto;
import com.PhishyLink.PhishingWebsiteDetection.entity.UrlData;

public class MaptoHistoryResponseDto {
    public  static HistoryResponseDto maptoHistoryResponse(UrlData urlData){

            HistoryResponseDto historyResponseDto = new HistoryResponseDto();
            historyResponseDto.setUrl(urlData.getUrl());
            historyResponseDto.setLabel(urlData.getLabel());
            historyResponseDto.setConfidence(urlData.getConfidence()*100);

            return historyResponseDto;
            }
}
