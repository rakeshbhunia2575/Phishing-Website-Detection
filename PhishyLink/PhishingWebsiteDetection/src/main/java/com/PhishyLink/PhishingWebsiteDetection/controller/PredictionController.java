package com.PhishyLink.PhishingWebsiteDetection.controller;

import com.PhishyLink.PhishingWebsiteDetection.dto.HistoryResponseDto;
import com.PhishyLink.PhishingWebsiteDetection.dto.RequestDto;
import com.PhishyLink.PhishingWebsiteDetection.dto.ResponseDto;
import com.PhishyLink.PhishingWebsiteDetection.service.PredictionService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

@Controller
@RequestMapping("/api/predict")
public class PredictionController {
        PredictionService predictionService;

    public PredictionController(PredictionService predictionService) {
        this.predictionService = predictionService;
    }

    @PostMapping
    public ResponseEntity<ResponseDto> getPrediction(@RequestBody RequestDto requestDto){
        System.out.println(requestDto.getUrlReq());
        return  ResponseEntity.status(HttpStatus.OK)
                               .body(predictionService.getPrediction(requestDto));
    }

    @GetMapping
    public ResponseEntity<List<HistoryResponseDto>> getHistory(){
        return  ResponseEntity.status(HttpStatus.OK)
                .body(predictionService.getHistory());
    }
}
