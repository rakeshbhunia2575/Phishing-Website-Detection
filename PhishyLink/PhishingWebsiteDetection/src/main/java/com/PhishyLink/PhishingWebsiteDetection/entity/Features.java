package com.PhishyLink.PhishingWebsiteDetection.entity;

import jakarta.persistence.*;

import java.util.Map;

@Entity
public class Features {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Integer having_IP_Address;
    private Integer URL_Length;
    private Integer Shortining_Service;
    private Integer having_At_Symbol;
    private Integer double_slash_redirecting;
    private Integer Prefix_Suffix;
    private Integer having_Sub_Domain;
    private Integer port;
    private Integer HTTPS_token;
    private Integer DNSRecord;
    private Integer SSLfinal_State;
    private Integer age_of_domain;
    private Integer Domain_registeration_length;
    private Integer Abnormal_URL;
    private Integer Redirect;
    private Integer Favicon;
    private Integer Request_URL;
    private Integer URL_of_Anchor;
    private Integer Links_in_tags;
    private Integer SFH;
    private Integer Submitting_to_email;
    private Integer on_mouseover;
    private Integer RightClick;
    private Integer popUpWidnow;
    private Integer Iframe;

    public Features(){}
    public Features(Long id, Integer having_IP_Address, Integer URL_Length,
                    Integer shortining_Service, Integer having_At_Symbol,
                    Integer double_slash_redirecting, Integer prefix_Suffix,
                    Integer having_Sub_Domain, Integer port, Integer HTTPS_token,
                    Integer DNSRecord, Integer SSLfinal_State, Integer age_of_domain,
                    Integer domain_registeration_length, Integer abnormal_URL,
                    Integer redirect, Integer favicon, Integer request_URL,
                    Integer URL_of_Anchor, Integer links_in_tags, Integer SFH,
                    Integer submitting_to_email, Integer on_mouseover,
                    Integer rightClick, Integer popUpWidnow, Integer iframe) {
        this.id = id;
        this.having_IP_Address = having_IP_Address;
        this.URL_Length = URL_Length;
        this.Shortining_Service = shortining_Service;
        this.having_At_Symbol = having_At_Symbol;
        this.double_slash_redirecting = double_slash_redirecting;
        this.Prefix_Suffix = prefix_Suffix;
        this.having_Sub_Domain = having_Sub_Domain;
        this.port = port;
        this.HTTPS_token = HTTPS_token;
        this.DNSRecord = DNSRecord;
        this.SSLfinal_State = SSLfinal_State;
        this.age_of_domain = age_of_domain;
        this.Domain_registeration_length = domain_registeration_length;
        this.Abnormal_URL = abnormal_URL;
        this.Redirect = redirect;
        this.Favicon = favicon;
        this.Request_URL = request_URL;
        this.URL_of_Anchor = URL_of_Anchor;
        this.Links_in_tags = links_in_tags;
        this.SFH = SFH;
        this.Submitting_to_email = submitting_to_email;
        this.on_mouseover = on_mouseover;
        this.RightClick = rightClick;
        this.popUpWidnow = popUpWidnow;
        this.Iframe = iframe;
    }

    public Features(Map<String,Integer> feature){
        this.having_IP_Address = feature.get("having_IP_Address");
        this.URL_Length = feature.get("URL_Length");
        this.Shortining_Service = feature.get("Shortining_Service");
        this.having_At_Symbol = feature.get("having_At_Symbol");
        this.double_slash_redirecting = feature.get("double_slash_redirecting");
        this.Prefix_Suffix = feature.get("Prefix_Suffix");
        this.having_Sub_Domain = feature.get("having_Sub_Domain");
        this.port = feature.get("port");
        this.HTTPS_token = feature.get("HTTPS_token");
        this.DNSRecord = feature.get("DNSRecord");
        this.SSLfinal_State = feature.get("SSLfinal_State");
        this.age_of_domain = feature.get("age_of_domain");
        this.Domain_registeration_length = feature.get("Domain_registeration_length");
        this.Abnormal_URL = feature.get("Abnormal_URL");
        this.Redirect = feature.get("Redirect");
        this.Favicon = feature.get("Favicon");
        this.Request_URL = feature.get("Request_URL");
        this.URL_of_Anchor = feature.get("URL_of_Anchor");
        this.Links_in_tags = feature.get("Links_in_tags");
        this.SFH = feature.get("SFH");
        this.Submitting_to_email = feature.get("Submitting_to_email");
        this.on_mouseover = feature.get("on_mouseover");
        this.RightClick = feature.get("RightClick");
        this.popUpWidnow = feature.get("popUpWidnow");
        this.Iframe = feature.get("Iframe");
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getHaving_IP_Address() {
        return having_IP_Address;
    }

    public void setHaving_IP_Address(Integer having_IP_Address) {
        this.having_IP_Address = having_IP_Address;
    }

    public Integer getURL_Length() {
        return URL_Length;
    }

    public void setURL_Length(Integer URL_Length) {
        this.URL_Length = URL_Length;
    }

    public Integer getShortining_Service() {
        return Shortining_Service;
    }

    public void setShortining_Service(Integer shortining_Service) {
        Shortining_Service = shortining_Service;
    }

    public Integer getHaving_At_Symbol() {
        return having_At_Symbol;
    }

    public void setHaving_At_Symbol(Integer having_At_Symbol) {
        this.having_At_Symbol = having_At_Symbol;
    }

    public Integer getDouble_slash_redirecting() {
        return double_slash_redirecting;
    }

    public void setDouble_slash_redirecting(Integer double_slash_redirecting) {
        this.double_slash_redirecting = double_slash_redirecting;
    }

    public Integer getPrefix_Suffix() {
        return Prefix_Suffix;
    }

    public void setPrefix_Suffix(Integer prefix_Suffix) {
        Prefix_Suffix = prefix_Suffix;
    }

    public Integer getHaving_Sub_Domain() {
        return having_Sub_Domain;
    }

    public void setHaving_Sub_Domain(Integer having_Sub_Domain) {
        this.having_Sub_Domain = having_Sub_Domain;
    }

    public Integer getPort() {
        return port;
    }

    public void setPort(Integer port) {
        this.port = port;
    }

    public Integer getHTTPS_token() {
        return HTTPS_token;
    }

    public void setHTTPS_token(Integer HTTPS_token) {
        this.HTTPS_token = HTTPS_token;
    }

    public Integer getDNSRecord() {
        return DNSRecord;
    }

    public void setDNSRecord(Integer DNSRecord) {
        this.DNSRecord = DNSRecord;
    }

    public Integer getSSLfinal_State() {
        return SSLfinal_State;
    }

    public void setSSLfinal_State(Integer SSLfinal_State) {
        this.SSLfinal_State = SSLfinal_State;
    }

    public Integer getAge_of_domain() {
        return age_of_domain;
    }

    public void setAge_of_domain(Integer age_of_domain) {
        this.age_of_domain = age_of_domain;
    }

    public Integer getDomain_registeration_length() {
        return Domain_registeration_length;
    }

    public void setDomain_registeration_length(Integer domain_registeration_length) {
        Domain_registeration_length = domain_registeration_length;
    }

    public Integer getAbnormal_URL() {
        return Abnormal_URL;
    }

    public void setAbnormal_URL(Integer abnormal_URL) {
        Abnormal_URL = abnormal_URL;
    }

    public Integer getRedirect() {
        return Redirect;
    }

    public void setRedirect(Integer redirect) {
        Redirect = redirect;
    }

    public Integer getFavicon() {
        return Favicon;
    }

    public void setFavicon(Integer favicon) {
        Favicon = favicon;
    }

    public Integer getRequest_URL() {
        return Request_URL;
    }

    public void setRequest_URL(Integer request_URL) {
        Request_URL = request_URL;
    }

    public Integer getURL_of_Anchor() {
        return URL_of_Anchor;
    }

    public void setURL_of_Anchor(Integer URL_of_Anchor) {
        this.URL_of_Anchor = URL_of_Anchor;
    }

    public Integer getLinks_in_tags() {
        return Links_in_tags;
    }

    public void setLinks_in_tags(Integer links_in_tags) {
        Links_in_tags = links_in_tags;
    }

    public Integer getSFH() {
        return SFH;
    }

    public void setSFH(Integer SFH) {
        this.SFH = SFH;
    }

    public Integer getSubmitting_to_email() {
        return Submitting_to_email;
    }

    public void setSubmitting_to_email(Integer submitting_to_email) {
        Submitting_to_email = submitting_to_email;
    }

    public Integer getOn_mouseover() {
        return on_mouseover;
    }

    public void setOn_mouseover(Integer on_mouseover) {
        this.on_mouseover = on_mouseover;
    }

    public Integer getRightClick() {
        return RightClick;
    }

    public void setRightClick(Integer rightClick) {
        RightClick = rightClick;
    }

    public Integer getPopUpWidnow() {
        return popUpWidnow;
    }

    public void setPopUpWidnow(Integer popUpWidnow) {
        this.popUpWidnow = popUpWidnow;
    }

    public Integer getIframe() {
        return Iframe;
    }

    public void setIframe(Integer iframe) {
        Iframe = iframe;
    }
}
