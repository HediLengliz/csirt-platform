"""Real-time anomaly detection and alert classification system."""

import os
import pickle
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from models.alert import AlertPriority
from models.event import Event, EventType


class RealTimeAnomalyDetector:
    """Real-time anomaly detection using Isolation Forest."""

    def __init__(
        self,
        model_path: str = "./models/anomaly_detector.pkl",
        contamination: float = 0.1,
    ):
        """Initialize the anomaly detector."""
        self.model_path = model_path
        self.contamination = contamination  # Expected proportion of anomalies
        self.model = None
        self.scaler = StandardScaler()
        self.feature_history = deque(maxlen=1000)  # Keep last 1000 events for training
        self.is_trained = False
        self._load_or_create_model()

    def _load_or_create_model(self):
        """Load existing model or create a new one."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    saved_data = pickle.load(f)
                    self.model = saved_data.get("model")
                    self.scaler = saved_data.get("scaler", StandardScaler())
                    self.is_trained = saved_data.get("is_trained", False)
                print(f"Loaded anomaly detection model from {self.model_path}")
            except Exception as e:
                print(f"Error loading model: {e}. Creating new model.")
                self._create_new_model()
        else:
            self._create_new_model()

    def _create_new_model(self):
        """Create a new anomaly detection model."""
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
            max_samples="auto",
        )
        self.is_trained = False
        print("Created new anomaly detection model")

    def extract_features(
        self, event: Event, context: Dict[str, Any] = None
    ) -> np.ndarray:
        """Extract features for anomaly detection."""
        context = context or {}

        # Event type encoding (one-hot like)
        event_type_map = {
            EventType.MALWARE_DETECTED: 1.0,
            EventType.UNAUTHORIZED_ACCESS: 0.9,
            EventType.DATA_EXFILTRATION: 0.95,
            EventType.BRUTE_FORCE: 0.7,
            EventType.DDoS: 0.8,
            EventType.SUSPICIOUS_ACTIVITY: 0.6,
            EventType.PHISHING: 0.5,
            EventType.LOGIN_FAILURE: 0.3,
            EventType.LOGIN_SUCCESS: 0.1,
            EventType.OTHER: 0.4,
        }
        event_type_score = event_type_map.get(event.event_type, 0.4)

        # Severity score
        severity = 0.0
        if event.severity_score:
            try:
                severity = float(event.severity_score)
                if severity > 10:
                    severity = severity / 10.0
            except:
                severity = event_type_score

        # Frequency features (log scale)
        source_ip_count = np.log1p(context.get("source_ip_count", 1))
        dest_ip_count = np.log1p(context.get("destination_ip_count", 1))
        user_count = np.log1p(context.get("user_count", 1))
        similar_events = np.log1p(context.get("similar_events_count", 0))

        # Time features
        try:
            if isinstance(event.timestamp, str):
                dt = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
            else:
                dt = event.timestamp
            hour = dt.hour / 24.0  # Normalize to 0-1
            day_of_week = dt.weekday() / 7.0  # Normalize to 0-1
        except:
            hour = 0.5
            day_of_week = 0.5

        # IP features (hash-based encoding)
        source_ip_hash = hash(event.source_ip or "unknown") % 1000 / 1000.0
        dest_ip_hash = hash(event.destination_ip or "unknown") % 1000 / 1000.0

        # Description length (anomalies often have longer descriptions)
        desc_length = len(event.description or "") / 500.0  # Normalize

        features = np.array(
            [
                [
                    event_type_score,
                    severity,
                    source_ip_count,
                    dest_ip_count,
                    user_count,
                    similar_events,
                    hour,
                    day_of_week,
                    source_ip_hash,
                    dest_ip_hash,
                    desc_length,
                ]
            ]
        )

        return features

    def detect_anomaly(
        self, event: Event, context: Dict[str, Any] = None
    ) -> Tuple[bool, float]:
        """Detect if event is an anomaly."""
        features = self.extract_features(event, context)

        # If not trained, use simple heuristic
        if not self.is_trained or self.model is None:
            return self._heuristic_anomaly_detection(event, context), 0.5

        try:
            # Scale features
            if hasattr(self.scaler, "mean_"):
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features

            # Predict anomaly (-1 for anomaly, 1 for normal)
            prediction = self.model.predict(features_scaled)[0]
            is_anomaly = prediction == -1

            # Get anomaly score (lower = more anomalous)
            anomaly_score = self.model.score_samples(features_scaled)[0]
            # Normalize to 0-1 (0 = most anomalous, 1 = most normal)
            normalized_score = 1.0 / (1.0 + np.exp(-anomaly_score))  # Sigmoid

            return is_anomaly, normalized_score
        except Exception as e:
            print(f"Error in anomaly detection: {e}")
            return self._heuristic_anomaly_detection(event, context), 0.5

    def _heuristic_anomaly_detection(
        self, event: Event, context: Dict[str, Any] = None
    ) -> bool:
        """Heuristic-based anomaly detection when model not trained."""
        context = context or {}

        # High severity events are likely anomalies
        if event.severity_score:
            try:
                if float(event.severity_score) >= 7.0:
                    return True
            except:
                pass

        # High frequency from same source
        if context.get("source_ip_count", 1) > 10:
            return True

        # Critical event types
        if event.event_type in [
            EventType.MALWARE_DETECTED,
            EventType.UNAUTHORIZED_ACCESS,
            EventType.DATA_EXFILTRATION,
        ]:
            return True

        return False

    def update_model(self, events: List[Event], contexts: List[Dict[str, Any]]):
        """Update the anomaly detection model with new data."""
        if len(events) < 10:
            return

        # Extract features for all events
        X = []
        for event, context in zip(events, contexts):
            features = self.extract_features(event, context)
            X.append(features[0])
            self.feature_history.append(features[0])

        X = np.array(X)

        # Fit scaler
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True

        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(
                {"model": self.model, "scaler": self.scaler, "is_trained": True}, f
            )

        print(f"Anomaly detection model updated with {len(events)} samples")


class AlertClassifier:
    """Automatic alert classification using clustering and pattern matching."""

    def __init__(self):
        """Initialize the classifier."""
        self.cluster_model = None
        self.patterns = {}  # Known attack patterns
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize known attack patterns."""
        self.patterns = {
            "ransomware": {
                "keywords": ["ransomware", "encrypt", "decrypt", "bitcoin", "payment"],
                "event_types": [EventType.MALWARE_DETECTED],
                "priority": AlertPriority.CRITICAL,
            },
            "brute_force": {
                "keywords": [
                    "failed",
                    "login",
                    "attempt",
                    "password",
                    "authentication",
                ],
                "event_types": [EventType.BRUTE_FORCE, EventType.LOGIN_FAILURE],
                "priority": AlertPriority.HIGH,
            },
            "data_exfiltration": {
                "keywords": ["exfiltrat", "data", "transfer", "large", "volume"],
                "event_types": [EventType.DATA_EXFILTRATION],
                "priority": AlertPriority.CRITICAL,
            },
            "ddos": {
                "keywords": ["ddos", "flood", "overload", "traffic", "bandwidth"],
                "event_types": [EventType.DDoS],
                "priority": AlertPriority.HIGH,
            },
            "phishing": {
                "keywords": ["phish", "email", "suspicious", "link", "attachment"],
                "event_types": [EventType.PHISHING],
                "priority": AlertPriority.MEDIUM,
            },
            "privilege_escalation": {
                "keywords": [
                    "privilege",
                    "escalation",
                    "sudo",
                    "admin",
                    "root",
                    "elevated",
                ],
                "event_types": [EventType.UNAUTHORIZED_ACCESS],
                "priority": AlertPriority.CRITICAL,
            },
        }

    def classify_alert(
        self, event: Event, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Classify alert based on patterns and context."""
        context = context or {}
        description = (event.description or "").lower()
        title = (getattr(event, "title", "") or "").lower()
        full_text = f"{title} {description}"

        classification = {
            "category": "unknown",
            "attack_type": None,
            "confidence": 0.0,
            "tags": [],
            "recommended_priority": None,
            "ioc": [],
        }

        # Pattern matching
        best_match = None
        best_score = 0.0

        for pattern_name, pattern in self.patterns.items():
            score = 0.0

            # Check event type match
            if event.event_type in pattern["event_types"]:
                score += 0.4

            # Check keyword matches
            keyword_matches = sum(1 for kw in pattern["keywords"] if kw in full_text)
            if keyword_matches > 0:
                score += (keyword_matches / len(pattern["keywords"])) * 0.6

            if score > best_score:
                best_score = score
                best_match = pattern_name

        if best_match and best_score > 0.3:
            pattern = self.patterns[best_match]
            classification["category"] = "attack"
            classification["attack_type"] = best_match
            classification["confidence"] = min(1.0, best_score)
            classification["tags"] = [best_match, "automated_detection"]
            classification["recommended_priority"] = pattern["priority"]

        # Extract IOCs (Indicators of Compromise)
        iocs = self._extract_iocs(event, full_text)
        classification["ioc"] = iocs

        # Add frequency-based tags
        if context.get("source_ip_count", 1) > 10:
            classification["tags"].append("high_frequency")
        if context.get("similar_events_count", 0) > 5:
            classification["tags"].append("recurring_pattern")

        return classification

    def _extract_iocs(self, event: Event, text: str) -> List[Dict[str, str]]:
        """Extract Indicators of Compromise from event."""
        import re

        iocs = []

        # IP addresses
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ips = re.findall(ip_pattern, text)
        for ip in set(ips):
            if ip not in ["127.0.0.1", "0.0.0.0"]:
                iocs.append({"type": "ip", "value": ip})

        # Add event IPs
        if event.source_ip and event.source_ip not in ["127.0.0.1", "0.0.0.0"]:
            iocs.append({"type": "ip", "value": event.source_ip})
        if event.destination_ip and event.destination_ip not in [
            "127.0.0.1",
            "0.0.0.0",
        ]:
            iocs.append({"type": "ip", "value": event.destination_ip})

        # Domains (simple pattern)
        domain_pattern = r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b"
        domains = re.findall(domain_pattern, text.lower())
        for domain in set(domains[:5]):  # Limit to 5
            if not domain.endswith(
                (".com", ".org", ".net", ".gov")
            ):  # Skip common TLDs
                iocs.append({"type": "domain", "value": domain})

        # Hashes (MD5, SHA1, SHA256)
        hash_patterns = {
            "md5": r"\b[a-f0-9]{32}\b",
            "sha1": r"\b[a-f0-9]{40}\b",
            "sha256": r"\b[a-f0-9]{64}\b",
        }
        for hash_type, pattern in hash_patterns.items():
            hashes = re.findall(pattern, text.lower())
            for h in set(hashes[:3]):  # Limit to 3 per type
                iocs.append({"type": hash_type, "value": h})

        # URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        for url in set(urls[:3]):  # Limit to 3
            iocs.append({"type": "url", "value": url})

        return iocs


class RealTimeMLSystem:
    """Main real-time ML system for detection and classification."""

    def __init__(self):
        """Initialize the real-time ML system."""
        self.anomaly_detector = RealTimeAnomalyDetector()
        self.classifier = AlertClassifier()
        self.event_window = deque(maxlen=100)  # Last 100 events for context
        self.context_cache = {}  # Cache context for recent events

    def process_event(
        self, event: Event, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process event in real-time and return ML insights."""
        context = context or {}

        # Store event in window
        self.event_window.append((event, context))

        # Anomaly detection
        is_anomaly, anomaly_score = self.anomaly_detector.detect_anomaly(event, context)

        # Alert classification
        classification = self.classifier.classify_alert(event, context)

        # Combine results
        result = {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "classification": classification,
            "ml_confidence": max(anomaly_score, classification["confidence"]),
            "recommended_action": self._recommend_action(is_anomaly, classification),
            "risk_level": self._calculate_risk_level(
                is_anomaly, anomaly_score, classification
            ),
        }

        return result

    def _recommend_action(
        self, is_anomaly: bool, classification: Dict[str, Any]
    ) -> str:
        """Recommend action based on detection results."""
        if not is_anomaly and classification["category"] == "unknown":
            return "monitor"

        if classification["attack_type"] == "ransomware":
            return "isolate_and_contain"
        elif classification["attack_type"] == "data_exfiltration":
            return "block_and_investigate"
        elif classification["attack_type"] == "brute_force":
            return "block_ip"
        elif classification["attack_type"] == "ddos":
            return "rate_limit"
        elif is_anomaly:
            return "investigate"
        else:
            return "review"

    def _calculate_risk_level(
        self, is_anomaly: bool, anomaly_score: float, classification: Dict[str, Any]
    ) -> str:
        """Calculate overall risk level."""
        if classification["recommended_priority"] == AlertPriority.CRITICAL:
            return "critical"
        elif classification["recommended_priority"] == AlertPriority.HIGH:
            return "high"
        elif is_anomaly and anomaly_score < 0.3:
            return "high"
        elif is_anomaly:
            return "medium"
        elif classification["category"] == "attack":
            return "medium"
        else:
            return "low"

    def update_models(self, events: List[Event], contexts: List[Dict[str, Any]]):
        """Update ML models with new training data."""
        self.anomaly_detector.update_model(events, contexts)
        print("ML models updated with new data")
