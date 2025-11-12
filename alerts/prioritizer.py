"""ML-based alert prioritization system with intelligent scoring."""

import os
import pickle
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from models.alert import AlertPriority
from models.event import Event, EventType


class AlertPrioritizer:
    """Machine learning model for alert prioritization with intelligent scoring."""

    def __init__(self, model_path: str = "./models/alert_prioritizer.pkl"):
        """Initialize the prioritizer."""
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = [
            "event_type_severity",
            "severity_score_numeric",
            "source_ip_frequency",
            "destination_ip_frequency",
            "user_frequency",
            "has_malware_keywords",
            "has_suspicious_patterns",
            "has_exploit_keywords",
            "has_privilege_escalation",
            "network_anomaly_score",
            "time_based_score",
            "source_reliability",
        ]
        self._load_or_create_model()

    def _load_or_create_model(self):
        """Load existing model or create a new one."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    saved_data = pickle.load(f)
                    self.model = saved_data.get("model")
                    self.scaler = saved_data.get("scaler", StandardScaler())
                    self.label_encoder = saved_data.get("label_encoder", LabelEncoder())
                print(f"Loaded ML model from {self.model_path}")
            except Exception as e:
                print(f"Error loading model: {e}. Creating new model.")
                self._create_new_model()
        else:
            self._create_new_model()

    def _create_new_model(self):
        """Create a new ML model."""
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            random_state=42,
            subsample=0.8,
        )
        print("Created new ML model")

    def _calculate_event_type_severity(self, event_type: EventType) -> float:
        """Calculate base severity score for event type."""
        severity_map = {
            EventType.MALWARE_DETECTED: 0.95,
            EventType.UNAUTHORIZED_ACCESS: 0.90,
            EventType.DATA_EXFILTRATION: 0.95,
            EventType.BRUTE_FORCE: 0.75,
            EventType.DDoS: 0.85,
            EventType.SUSPICIOUS_ACTIVITY: 0.70,
            EventType.PHISHING: 0.65,
            EventType.LOGIN_FAILURE: 0.40,
            EventType.LOGIN_SUCCESS: 0.10,
            EventType.OTHER: 0.50,
        }
        return severity_map.get(event_type, 0.50)

    def _detect_keywords(self, text: str, keyword_lists: List[List[str]]) -> List[int]:
        """Detect presence of keywords in text."""
        if not text:
            return [0] * len(keyword_lists)

        text_lower = text.lower()
        results = []
        for keywords in keyword_lists:
            results.append(int(any(keyword in text_lower for keyword in keywords)))
        return results

    def _calculate_network_anomaly_score(self, context: Dict[str, Any]) -> float:
        """Calculate network anomaly score based on frequency patterns."""
        source_ip_count = context.get("source_ip_count", 1)
        destination_ip_count = context.get("destination_ip_count", 1)
        user_count = context.get("user_count", 1)

        # High frequency from same source = suspicious
        if source_ip_count > 10:
            return min(0.9, 0.5 + (source_ip_count - 10) * 0.05)
        elif source_ip_count > 5:
            return 0.6
        elif source_ip_count > 2:
            return 0.4

        # Multiple destinations from same source = suspicious
        if destination_ip_count > 5:
            return min(0.85, 0.5 + (destination_ip_count - 5) * 0.05)

        # Multiple users from same IP = suspicious
        if user_count > 3:
            return min(0.8, 0.5 + (user_count - 3) * 0.05)

        return 0.3

    def _calculate_time_based_score(self, event: Event) -> float:
        """Calculate score based on time patterns."""
        try:
            if event.timestamp:
                # Parse timestamp
                if isinstance(event.timestamp, str):
                    dt = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
                else:
                    dt = event.timestamp

                hour = dt.hour
                # Off-hours activity is more suspicious
                if hour < 6 or hour > 22:
                    return 0.7
                elif hour < 8 or hour > 20:
                    return 0.5
                else:
                    return 0.3
        except:
            pass
        return 0.4

    def _calculate_source_reliability(self, source: str) -> float:
        """Calculate reliability score based on source."""
        # More reliable sources get higher base scores
        reliability_map = {
            "splunk": 0.8,
            "elastic": 0.8,
            "ids_ips": 0.85,
            "firewall": 0.75,
            "endpoint": 0.70,
            "network": 0.65,
            "custom": 0.50,
        }
        return reliability_map.get(source.lower(), 0.50)

    def extract_features(
        self, event: Event, context: Dict[str, Any] = None
    ) -> np.ndarray:
        """Extract intelligent features from event for ML model."""
        context = context or {}

        # Base event type severity
        event_type_severity = self._calculate_event_type_severity(event.event_type)

        # Parse severity score
        severity_score_numeric = 0.0
        if event.severity_score:
            try:
                severity_score_numeric = float(event.severity_score)
                # Normalize to 0-1 range if needed
                if severity_score_numeric > 10:
                    severity_score_numeric = severity_score_numeric / 10.0
            except (ValueError, TypeError):
                severity_score_numeric = event_type_severity

        # Frequency-based features (log scale to prevent outliers)
        source_ip_frequency = np.log1p(context.get("source_ip_count", 1))
        destination_ip_frequency = np.log1p(context.get("destination_ip_count", 1))
        user_frequency = np.log1p(context.get("user_count", 1))

        # Keyword detection
        description = (event.description or "").lower()
        title = (getattr(event, "title", "") or "").lower()
        full_text = f"{title} {description}"

        malware_keywords = [
            "malware",
            "virus",
            "trojan",
            "ransomware",
            "rootkit",
            "backdoor",
            "spyware",
        ]
        suspicious_patterns = [
            "unauthorized",
            "breach",
            "exploit",
            "attack",
            "intrusion",
            "compromise",
        ]
        exploit_keywords = [
            "exploit",
            "cve-",
            "vulnerability",
            "zero-day",
            "rce",
            "sql injection",
        ]
        privilege_keywords = [
            "privilege",
            "escalation",
            "sudo",
            "admin",
            "root",
            "administrator",
        ]

        has_malware = int(any(kw in full_text for kw in malware_keywords))
        has_suspicious = int(any(kw in full_text for kw in suspicious_patterns))
        has_exploit = int(any(kw in full_text for kw in exploit_keywords))
        has_privilege = int(any(kw in full_text for kw in privilege_keywords))

        # Network anomaly score
        network_anomaly = self._calculate_network_anomaly_score(context)

        # Time-based score
        time_score = self._calculate_time_based_score(event)

        # Source reliability
        source_reliability = self._calculate_source_reliability(
            event.source.value if hasattr(event.source, "value") else str(event.source)
        )

        features = np.array(
            [
                [
                    event_type_severity,
                    severity_score_numeric,
                    source_ip_frequency,
                    destination_ip_frequency,
                    user_frequency,
                    has_malware,
                    has_suspicious,
                    has_exploit,
                    has_privilege,
                    network_anomaly,
                    time_score,
                    source_reliability,
                ]
            ]
        )

        return features

    def _calculate_intelligent_score(
        self, event: Event, context: Dict[str, Any] = None
    ) -> float:
        """Calculate intelligent ML score without requiring trained model."""
        features = self.extract_features(event, context)

        event_type_severity = features[0][0]
        severity_score_raw = features[0][1]
        source_ip_freq = features[0][2]  # log scale
        dest_ip_freq = features[0][3]  # log scale
        user_freq = features[0][4]  # log scale
        has_malware = features[0][5]
        has_suspicious = features[0][6]
        has_exploit = features[0][7]
        has_privilege = features[0][8]
        network_anomaly = features[0][9]
        time_score = features[0][10]
        source_reliability = features[0][11]

        # Normalize severity score to 0-1 range
        if severity_score_raw > 1.0:
            severity_score = min(1.0, severity_score_raw / 10.0)
        elif severity_score_raw <= 0:
            severity_score = event_type_severity  # Fallback to event type
        else:
            severity_score = severity_score_raw

        # Start with event type as base (40% of final score)
        base_score = event_type_severity * 0.40

        # Add severity contribution (30% of final score)
        base_score += severity_score * 0.30

        # Keyword multiplier (not additive - multiplies the risk)
        keyword_multiplier = 1.0
        if has_malware:
            keyword_multiplier += 0.25  # +25% risk
        if has_exploit:
            keyword_multiplier += 0.20  # +20% risk
        if has_privilege:
            keyword_multiplier += 0.15  # +15% risk
        if has_suspicious:
            keyword_multiplier += 0.10  # +10% risk
        # Cap multiplier at 1.6 (60% increase)
        keyword_multiplier = min(1.6, keyword_multiplier)

        # Apply keyword multiplier to base score
        base_score = base_score * keyword_multiplier

        # Add network anomaly (15% of range)
        # Network anomaly is already 0-0.9, scale it to contribute up to 15% of score
        base_score += network_anomaly * 0.15

        # Frequency contribution (10% of range)
        # Convert log frequencies to risk score
        # log1p(1) ≈ 0.69, log1p(5) ≈ 1.79, log1p(10) ≈ 2.40, log1p(20) ≈ 3.04
        avg_freq_log = (source_ip_freq + dest_ip_freq + user_freq) / 3.0
        if avg_freq_log > 2.8:  # Very high frequency (log1p(15+))
            freq_contrib = 0.10
        elif avg_freq_log > 2.2:  # High frequency (log1p(8+))
            freq_contrib = 0.07
        elif avg_freq_log > 1.5:  # Medium frequency (log1p(3+))
            freq_contrib = 0.04
        elif avg_freq_log > 0.7:  # Low frequency (log1p(1+))
            freq_contrib = 0.02
        else:
            freq_contrib = 0.0
        base_score += freq_contrib

        # Time-based adjustment (5% of range)
        # Off-hours adds risk, business hours reduces it slightly
        time_adjustment = (time_score - 0.4) * 0.05  # -0.005 to +0.015
        base_score += time_adjustment

        # Source reliability adjustment (small)
        # More reliable sources get slight boost
        source_adjustment = (source_reliability - 0.65) * 0.02  # -0.003 to +0.004
        base_score += source_adjustment

        # Apply sigmoid-like compression to prevent scores > 0.95
        # Scores above 0.90 get compressed more aggressively
        if base_score > 0.90:
            excess = base_score - 0.90
            base_score = 0.90 + (excess * 0.33)  # Compress excess by 67%
        elif base_score > 0.85:
            excess = base_score - 0.85
            base_score = 0.85 + (excess * 0.50)  # Compress excess by 50%

        # Ensure minimum score based on event type
        min_score = max(
            0.10, event_type_severity * 0.5
        )  # At least 50% of base severity
        max_score = min(0.95, event_type_severity * 1.2)  # Cap at 120% of base severity

        # Final normalization with event-type-based bounds
        intelligent_score = max(min_score, min(max_score, base_score))

        return intelligent_score

    def predict_priority(
        self, event: Event, context: Dict[str, Any] = None
    ) -> Tuple[AlertPriority, float]:
        """Predict alert priority using ML model or intelligent scoring."""
        features = self.extract_features(event, context)

        # Try to use trained model if available
        if hasattr(self.model, "classes_") and len(self.model.classes_) > 0:
            try:
                # Scale features if scaler is fitted
                if hasattr(self.scaler, "mean_"):
                    features_scaled = self.scaler.transform(features)
                else:
                    features_scaled = features

                # Predict probability
                probabilities = self.model.predict_proba(features_scaled)[0]
                predicted_class_idx = np.argmax(probabilities)
                confidence = float(probabilities[predicted_class_idx])

                # Map to AlertPriority
                priority_mapping = {
                    0: AlertPriority.CRITICAL,
                    1: AlertPriority.HIGH,
                    2: AlertPriority.MEDIUM,
                    3: AlertPriority.LOW,
                    4: AlertPriority.INFO,
                }

                priority = priority_mapping.get(
                    predicted_class_idx, AlertPriority.MEDIUM
                )

                # Use confidence as ML score, but ensure it's meaningful
                ml_score = max(confidence, 0.6)  # Minimum 60% confidence

                return priority, ml_score
            except Exception as e:
                print(f"Error in ML prediction: {e}. Using intelligent scoring.")

        # Fallback to intelligent scoring
        intelligent_score = self._calculate_intelligent_score(event, context)
        priority = self._intelligent_priority_mapping(intelligent_score)

        return priority, intelligent_score

    def _intelligent_priority_mapping(self, score: float) -> AlertPriority:
        """Map intelligent score to priority level."""
        # More granular mapping for better distribution
        if score >= 0.88:
            return AlertPriority.CRITICAL
        elif score >= 0.72:
            return AlertPriority.HIGH
        elif score >= 0.52:
            return AlertPriority.MEDIUM
        elif score >= 0.32:
            return AlertPriority.LOW
        else:
            return AlertPriority.INFO

    def _rule_based_priority(self, event: Event) -> AlertPriority:
        """Rule-based priority fallback."""
        # Critical events
        if event.event_type in [
            EventType.MALWARE_DETECTED,
            EventType.UNAUTHORIZED_ACCESS,
            EventType.DATA_EXFILTRATION,
        ]:
            return AlertPriority.CRITICAL

        # High priority
        if event.event_type in [
            EventType.SUSPICIOUS_ACTIVITY,
            EventType.BRUTE_FORCE,
            EventType.DDoS,
        ]:
            return AlertPriority.HIGH

        # Medium priority
        if event.event_type in [EventType.LOGIN_FAILURE, EventType.PHISHING]:
            return AlertPriority.MEDIUM

        # Low priority
        if event.event_type == EventType.LOGIN_SUCCESS:
            return AlertPriority.LOW

        return AlertPriority.INFO

    def train(self, training_data: List[Dict[str, Any]]):
        """Train the ML model with labeled data."""
        if not training_data or len(training_data) < 10:
            print("Insufficient training data. Need at least 10 samples.")
            return

        # Prepare data
        X = []
        y = []

        for row in training_data:
            # Extract features from training data
            features = self.extract_features_from_dict(row)
            X.append(features[0])
            priority = row.get("priority")
            if priority:
                y.append(priority)

        if len(X) < 10:
            print("Insufficient valid training data.")
            return

        X = np.array(X)
        y = np.array(y)

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42
        )

        # Train model
        self.model.fit(X_train, y_train)

        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        print(
            f"Model training complete. Train accuracy: {train_score:.2f}, Test accuracy: {test_score:.2f}"
        )

        # Save model with scaler and encoder
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(
                {
                    "model": self.model,
                    "scaler": self.scaler,
                    "label_encoder": self.label_encoder,
                },
                f,
            )
        print(f"Model saved to {self.model_path}")

    def extract_features_from_dict(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract features from dictionary (for training)."""

        # Create a mock event-like structure
        class MockEvent:
            def __init__(self, data):
                self.event_type = EventType(data.get("event_type", "other"))
                self.source = type(
                    "obj", (object,), {"value": data.get("source", "custom")}
                )()
                self.description = data.get("description", "")
                self.severity_score = data.get("severity_score")
                self.timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        event = MockEvent(data)
        context = {
            "source_ip_count": data.get("source_ip_count", 1),
            "destination_ip_count": data.get("destination_ip_count", 1),
            "user_count": data.get("user_count", 1),
        }

        return self.extract_features(event, context)
