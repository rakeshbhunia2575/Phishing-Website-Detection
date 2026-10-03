package com.PhishyLink.PhishingWebsiteDetection.mapping;

import com.PhishyLink.PhishingWebsiteDetection.dto.ResponseDto;
import com.PhishyLink.PhishingWebsiteDetection.entity.FastApiResponse;

public class MapToResponseDto {
    public static ResponseDto mapToResponse(FastApiResponse fastApiResponse){

        ResponseDto responseDto = new ResponseDto();

        responseDto.setLabel(fastApiResponse.getLabel());

        responseDto.setUrl(fastApiResponse.getUrl());

        if (fastApiResponse.getNotes() != null && !fastApiResponse.getNotes().isEmpty()) {
            responseDto.setNotes(fastApiResponse.getNotes().getFirst());
        } else {
            responseDto.setNotes("");
        }

        if(fastApiResponse.getReasons() != null && !fastApiResponse.getReasons().isEmpty()){
            responseDto.setReason(fastApiResponse.getReasons().getFirst());
        }
        else{
            responseDto.setReason("");
        }

        if(fastApiResponse.getLabel().equals("Legitimate Website")) {
            if(fastApiResponse.getTier().equals("lexical")){
                responseDto.setMessage("The website could be malicious try to avoid it.");
            }
            else{
                responseDto.setMessage("This website is good to go.");
            }
        }
        else {
            responseDto.setMessage("The website is malicious. Avoid it .");
        }

        return responseDto;
    }
}
