package com.PhishyLink.PhishingWebsiteDetection.repository;

import com.PhishyLink.PhishingWebsiteDetection.entity.UrlData;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

//@Repository
public interface PredictionRepository  extends JpaRepository<UrlData,Long> {
    boolean existsByUrl(String url);
    List<UrlData> findTop15ByOrderByIdDesc();
}
