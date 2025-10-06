"""
Data Validator

Validates and assesses the quality of collected data.
Provides scoring and filtering capabilities for data quality assurance.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import re
import json
from dataclasses import dataclass
from enum import Enum

from .base_collector import CollectedData, DataSource


class ValidationLevel(Enum):
    """Validation levels for data quality assessment."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    quality_score: float
    relevance_score: float
    completeness_score: float
    recency_score: float
    authority_score: float
    issues: List[str]
    recommendations: List[str]
    validation_level: ValidationLevel
    validated_at: datetime


class DataValidator:
    """Validates and assesses the quality of collected data."""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        self.quality_thresholds = self._get_quality_thresholds()
    
    def _get_quality_thresholds(self) -> Dict[str, float]:
        """Get quality thresholds based on validation level."""
        if self.validation_level == ValidationLevel.BASIC:
            return {
                "min_quality": 0.3,
                "min_relevance": 0.3,
                "min_completeness": 0.3,
                "min_recency": 0.2,
                "min_authority": 0.3
            }
        elif self.validation_level == ValidationLevel.STRICT:
            return {
                "min_quality": 0.8,
                "min_relevance": 0.7,
                "min_completeness": 0.8,
                "min_recency": 0.7,
                "min_authority": 0.8
            }
        else:  # STANDARD
            return {
                "min_quality": 0.6,
                "min_relevance": 0.5,
                "min_completeness": 0.6,
                "min_recency": 0.5,
                "min_authority": 0.6
            }
    
    def validate_data(self, data: CollectedData) -> ValidationResult:
        """
        Validate a single collected data item.
        
        Args:
            data: Collected data item to validate
            
        Returns:
            Validation result with scores and recommendations
        """
        issues = []
        recommendations = []
        
        # Calculate individual scores
        quality_score = self._calculate_quality_score(data)
        relevance_score = self._calculate_relevance_score(data)
        completeness_score = self._calculate_completeness_score(data)
        recency_score = self._calculate_recency_score(data)
        authority_score = self._calculate_authority_score(data)
        
        # Check against thresholds
        thresholds = self.quality_thresholds
        
        if quality_score < thresholds["min_quality"]:
            issues.append(f"Quality score {quality_score:.2f} below threshold {thresholds['min_quality']}")
            recommendations.append("Improve data quality by ensuring accurate and complete information")
        
        if relevance_score < thresholds["min_relevance"]:
            issues.append(f"Relevance score {relevance_score:.2f} below threshold {thresholds['min_relevance']}")
            recommendations.append("Ensure data is directly relevant to the research query")
        
        if completeness_score < thresholds["min_completeness"]:
            issues.append(f"Completeness score {completeness_score:.2f} below threshold {thresholds['min_completeness']}")
            recommendations.append("Provide more complete data with all required fields")
        
        if recency_score < thresholds["min_recency"]:
            issues.append(f"Recency score {recency_score:.2f} below threshold {thresholds['min_recency']}")
            recommendations.append("Use more recent data sources")
        
        if authority_score < thresholds["min_authority"]:
            issues.append(f"Authority score {authority_score:.2f} below threshold {thresholds['min_authority']}")
            recommendations.append("Use more authoritative and reliable sources")
        
        # Overall validation
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            recency_score=recency_score,
            authority_score=authority_score,
            issues=issues,
            recommendations=recommendations,
            validation_level=self.validation_level,
            validated_at=datetime.now()
        )
    
    def validate_dataset(self, dataset: List[CollectedData]) -> Dict[str, Any]:
        """
        Validate an entire dataset.
        
        Args:
            dataset: List of collected data items
            
        Returns:
            Dataset validation summary
        """
        if not dataset:
            return {
                "total_items": 0,
                "valid_items": 0,
                "invalid_items": 0,
                "average_quality": 0.0,
                "validation_summary": "No data to validate"
            }
        
        validation_results = []
        valid_count = 0
        total_quality = 0.0
        
        for data_item in dataset:
            result = self.validate_data(data_item)
            validation_results.append(result)
            
            if result.is_valid:
                valid_count += 1
            
            total_quality += result.quality_score
        
        invalid_count = len(dataset) - valid_count
        average_quality = total_quality / len(dataset)
        
        # Analyze common issues
        all_issues = []
        for result in validation_results:
            all_issues.extend(result.issues)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Get top issues
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_items": len(dataset),
            "valid_items": valid_count,
            "invalid_items": invalid_count,
            "validation_rate": valid_count / len(dataset),
            "average_quality": round(average_quality, 3),
            "top_issues": top_issues,
            "validation_level": self.validation_level.value,
            "validated_at": datetime.now().isoformat()
        }
    
    def filter_high_quality_data(self, dataset: List[CollectedData], min_quality: float = 0.7) -> List[CollectedData]:
        """
        Filter dataset to include only high-quality data.
        
        Args:
            dataset: List of collected data items
            min_quality: Minimum quality score threshold
            
        Returns:
            Filtered list of high-quality data items
        """
        high_quality_data = []
        
        for data_item in dataset:
            result = self.validate_data(data_item)
            if result.quality_score >= min_quality and result.is_valid:
                high_quality_data.append(data_item)
        
        return high_quality_data
    
    def _calculate_quality_score(self, data: CollectedData) -> float:
        """Calculate overall quality score for data."""
        score = 0.0
        
        # Base score from source reliability
        score += data.source.reliability_score * 0.3
        
        # Data completeness
        if isinstance(data.data, dict):
            if len(data.data) > 0:
                score += 0.2
            if any(key in data.data for key in ['title', 'name', 'description']):
                score += 0.2
            if any(key in data.data for key in ['date', 'timestamp', 'published']):
                score += 0.1
        elif isinstance(data.data, list):
            if len(data.data) > 0:
                score += 0.2
        elif isinstance(data.data, str):
            if len(data.data) > 50:  # Substantial content
                score += 0.2
        
        # Processing notes indicate good data handling
        if data.processing_notes and len(data.processing_notes) > 0:
            score += 0.1
        
        # Raw response availability
        if data.raw_response:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_relevance_score(self, data: CollectedData) -> float:
        """Calculate relevance score for data."""
        # Use the relevance score already calculated during collection
        return data.relevance_score
    
    def _calculate_completeness_score(self, data: CollectedData) -> float:
        """Calculate completeness score for data."""
        score = 0.0
        
        if isinstance(data.data, dict):
            # Check for essential fields based on data type
            if data.data_type == "academic_paper":
                essential_fields = ['title', 'authors', 'abstract']
            elif data.data_type == "news_article":
                essential_fields = ['title', 'description', 'published_date']
            elif data.data_type == "financial_data":
                essential_fields = ['ticker', 'company_name', 'current_price']
            elif data.data_type == "government_data":
                essential_fields = ['title', 'value', 'date']
            else:
                essential_fields = ['title', 'description']
            
            present_fields = sum(1 for field in essential_fields if field in data.data and data.data[field])
            score = present_fields / len(essential_fields)
        
        elif isinstance(data.data, list):
            score = 0.8 if len(data.data) > 0 else 0.0
        
        elif isinstance(data.data, str):
            score = 0.6 if len(data.data) > 100 else 0.3
        
        return score
    
    def _calculate_recency_score(self, data: CollectedData) -> float:
        """Calculate recency score for data."""
        # Check if data has date information
        if isinstance(data.data, dict):
            date_fields = ['date', 'timestamp', 'published_date', 'created_at']
            for field in date_fields:
                if field in data.data:
                    date_str = data.data[field]
                    try:
                        # Try to parse the date
                        if isinstance(date_str, str):
                            # Handle various date formats
                            date_obj = self._parse_date(date_str)
                            if date_obj:
                                days_old = (datetime.now() - date_obj).days
                                
                                # Score based on age
                                if days_old <= 30:
                                    return 1.0
                                elif days_old <= 90:
                                    return 0.8
                                elif days_old <= 365:
                                    return 0.6
                                elif days_old <= 730:
                                    return 0.4
                                else:
                                    return 0.2
                    except:
                        continue
        
        # If no date found, use collection timestamp
        days_since_collection = (datetime.now() - data.collected_at).days
        if days_since_collection <= 1:
            return 0.9
        elif days_since_collection <= 7:
            return 0.7
        elif days_since_collection <= 30:
            return 0.5
        else:
            return 0.3
    
    def _calculate_authority_score(self, data: CollectedData) -> float:
        """Calculate authority score for data."""
        score = data.source.reliability_score
        
        # Adjust based on data source characteristics
        if data.source.category == "government":
            score += 0.1
        elif data.source.category == "academic":
            score += 0.1
        elif data.source.category == "financial":
            score += 0.05
        
        # Check for official indicators in data
        if isinstance(data.data, dict):
            data_text = ' '.join(str(v) for v in data.data.values()).lower()
            if any(indicator in data_text for indicator in ['official', 'government', 'federal', 'sec', 'fda']):
                score += 0.1
        
        return min(score, 1.0)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats."""
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try to extract year from string
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            year = int(year_match.group())
            return datetime(year, 1, 1)
        
        return None
    
    def generate_quality_report(self, dataset: List[CollectedData]) -> Dict[str, Any]:
        """
        Generate a comprehensive quality report for a dataset.
        
        Args:
            dataset: List of collected data items
            
        Returns:
            Comprehensive quality report
        """
        validation_summary = self.validate_dataset(dataset)
        
        # Analyze by data type
        data_types = {}
        for data_item in dataset:
            data_type = data_item.data_type
            if data_type not in data_types:
                data_types[data_type] = []
            data_types[data_type].append(data_item)
        
        type_analysis = {}
        for data_type, items in data_types.items():
            type_validation = self.validate_dataset(items)
            type_analysis[data_type] = {
                "count": len(items),
                "average_quality": type_validation["average_quality"],
                "validation_rate": type_validation["validation_rate"]
            }
        
        # Analyze by source
        sources = {}
        for data_item in dataset:
            source_name = data_item.source.name
            if source_name not in sources:
                sources[source_name] = []
            sources[source_name].append(data_item)
        
        source_analysis = {}
        for source_name, items in sources.items():
            source_validation = self.validate_dataset(items)
            source_analysis[source_name] = {
                "count": len(items),
                "average_quality": source_validation["average_quality"],
                "validation_rate": source_validation["validation_rate"],
                "reliability_score": items[0].source.reliability_score if items else 0.0
            }
        
        return {
            "overall_summary": validation_summary,
            "data_type_analysis": type_analysis,
            "source_analysis": source_analysis,
            "recommendations": self._generate_recommendations(validation_summary, type_analysis, source_analysis),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, 
                                validation_summary: Dict[str, Any],
                                type_analysis: Dict[str, Any],
                                source_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Overall recommendations
        if validation_summary["validation_rate"] < 0.7:
            recommendations.append("Overall data quality is below 70%. Consider improving data collection processes.")
        
        if validation_summary["average_quality"] < 0.6:
            recommendations.append("Average data quality is low. Focus on using more reliable sources.")
        
        # Data type recommendations
        for data_type, analysis in type_analysis.items():
            if analysis["validation_rate"] < 0.5:
                recommendations.append(f"Data type '{data_type}' has low validation rate. Review collection methods.")
        
        # Source recommendations
        for source_name, analysis in source_analysis.items():
            if analysis["average_quality"] < 0.5:
                recommendations.append(f"Source '{source_name}' produces low-quality data. Consider alternative sources.")
        
        return recommendations
