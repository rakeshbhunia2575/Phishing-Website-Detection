package com.PhishyLink.PhishingWebsiteDetection.repository;

import com.PhishyLink.PhishingWebsiteDetection.entity.Features;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FeaturesData extends JpaRepository<Features,Long> {
}
