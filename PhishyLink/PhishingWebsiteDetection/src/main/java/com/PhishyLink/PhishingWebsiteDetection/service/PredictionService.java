package com.PhishyLink.PhishingWebsiteDetection.service;

import com.PhishyLink.PhishingWebsiteDetection.dto.HistoryResponseDto;
import com.PhishyLink.PhishingWebsiteDetection.dto.RequestDto;
import com.PhishyLink.PhishingWebsiteDetection.dto.ResponseDto;
import com.PhishyLink.PhishingWebsiteDetection.entity.FastApiResponse;
import com.PhishyLink.PhishingWebsiteDetection.entity.Features;
import com.PhishyLink.PhishingWebsiteDetection.entity.UrlData;
import com.PhishyLink.PhishingWebsiteDetection.exceptions.InvalidUrlException;
import com.PhishyLink.PhishingWebsiteDetection.exceptions.OutOfServiceException;
import com.PhishyLink.PhishingWebsiteDetection.mapping.MapToResponseDto;
import com.PhishyLink.PhishingWebsiteDetection.mapping.MaptoHistoryResponseDto;
import com.PhishyLink.PhishingWebsiteDetection.mapping.MaptoUrl;
import com.PhishyLink.PhishingWebsiteDetection.repository.FeaturesData;
import com.PhishyLink.PhishingWebsiteDetection.repository.PredictionRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.MediaType;

import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;

@Service
public class PredictionService {
    private PredictionRepository predictionRepository;
    private FeaturesData featuresData;

    @Value("${fastapi.url}")
    private String fastApiUrl;

    public PredictionService(PredictionRepository predictionRepository, FeaturesData featuresData) {
        this.predictionRepository = predictionRepository;
        this.featuresData = featuresData;
    }

    public ResponseDto getPrediction(RequestDto requestDto){
        String reqUrl = requestDto.getUrlReq();
        if (reqUrl == null || reqUrl.isBlank()) {
            throw new InvalidUrlException("URL is missing in the request body");
        }

        try {

            SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
            factory.setConnectTimeout(10_000);
            factory.setReadTimeout(90_000);   // long enough for a sleeping FastAPI to wake up
            RestClient client = RestClient.builder()
                    .baseUrl(fastApiUrl)
                    .requestFactory(factory)
                    .build();
            FastApiResponse fastApiResponse = client.post()
                    .uri("/predict")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of("url", reqUrl))
                    .retrieve()
                    .body(FastApiResponse.class);

            UrlData urlData = MaptoUrl.maptoUrl(fastApiResponse);
            if (!predictionRepository.existsByUrl(urlData.getUrl())) {
                try {
                    predictionRepository.save(urlData);
                    featuresData.save(new Features(fastApiResponse.getFeatures()));
                } catch (DataIntegrityViolationException e) {
                    // another request saved the same URL at the same moment: ignore
                }
            }
            return MapToResponseDto.mapToResponse(fastApiResponse);
        }
        catch (HttpClientErrorException.BadRequest e){
            throw  new InvalidUrlException("Invalid Url "+reqUrl);
        } catch (HttpServerErrorException.InternalServerError e) {
            throw new OutOfServiceException("The remote server returned an internal server error");
        }catch (ResourceAccessException e) {
            throw new OutOfServiceException("Prediction service is unavailable");
        }

    }

    public List<HistoryResponseDto> getHistory(){
        List<UrlData> urls = predictionRepository.findTop15ByOrderByIdDesc();

        return urls.stream()
                .map(MaptoHistoryResponseDto::maptoHistoryResponse)
                .toList();
    }
}
