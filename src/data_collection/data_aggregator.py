"""
Data Aggregator

Aggregates and consolidates data from multiple collectors.
Provides deduplication, merging, and cross-referencing capabilities.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import hashlib
import json
from dataclasses import dataclass, field
from collections import defaultdict

from .base_collector import CollectedData, DataSource
from .data_validator import DataValidator, ValidationLevel


@dataclass
class AggregationConfig:
    """Configuration for data aggregation."""
    enable_deduplication: bool = True
    enable_cross_referencing: bool = True
    enable_merging: bool = True
    similarity_threshold: float = 0.8
    max_duplicates: int = 5
    validation_level: ValidationLevel = ValidationLevel.STANDARD


@dataclass
class AggregatedData:
    """Aggregated data item with metadata."""
    id: str
    title: str
    description: str
    data_type: str
    aggregated_data: Dict[str, Any]
    source_data: List[CollectedData]
    cross_references: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class DataAggregator:
    """Aggregates and consolidates data from multiple collectors."""
    
    def __init__(self, config: Optional[AggregationConfig] = None):
        self.config = config or AggregationConfig()
        self.validator = DataValidator(self.config.validation_level)
        self.aggregated_items: Dict[str, AggregatedData] = {}
        self.deduplication_cache: Dict[str, List[str]] = defaultdict(list)
    
    def aggregate_data(self, 
                      datasets: Dict[str, List[CollectedData]], 
                      research_context: Optional[Dict[str, Any]] = None) -> List[AggregatedData]:
        """
        Aggregate data from multiple collectors.
        
        Args:
            datasets: Dictionary mapping collector names to their collected data
            research_context: Optional research context for better aggregation
            
        Returns:
            List of aggregated data items
        """
        print(f">>> DataAggregator: Starting aggregation of {sum(len(data) for data in datasets.values())} items from {len(datasets)} collectors")
        
        # Step 1: Validate all data
        all_data = []
        for collector_name, data_list in datasets.items():
            print(f"   Validating {len(data_list)} items from {collector_name}")
            validated_data = self.validator.filter_high_quality_data(data_list)
            all_data.extend(validated_data)
            print(f"   Kept {len(validated_data)} high-quality items from {collector_name}")
        
        print(f"   Total high-quality items after validation: {len(all_data)}")
        
        # Step 2: Group by data type
        data_by_type = self._group_by_data_type(all_data)
        print(f"   Grouped into {len(data_by_type)} data types")
        
        # Step 3: Process each data type
        aggregated_results = []
        for data_type, items in data_by_type.items():
            print(f"   Processing {len(items)} items of type '{data_type}'")
            
            if self.config.enable_deduplication:
                deduplicated_items = self._deduplicate_data(items)
                print(f"   Deduplicated to {len(deduplicated_items)} unique items")
            else:
                deduplicated_items = items
            
            if self.config.enable_merging:
                merged_items = self._merge_similar_data(deduplicated_items)
                print(f"   Merged to {len(merged_items)} consolidated items")
            else:
                merged_items = deduplicated_items
            
            # Create aggregated data items
            for item in merged_items:
                aggregated_item = self._create_aggregated_item(item, research_context)
                aggregated_results.append(aggregated_item)
                self.aggregated_items[aggregated_item.id] = aggregated_item
        
        print(f">>> DataAggregator: Aggregation complete. Created {len(aggregated_results)} aggregated items")
        return aggregated_results
    
    def _group_by_data_type(self, data_items: List[CollectedData]) -> Dict[str, List[CollectedData]]:
        """Group data items by their data type."""
        grouped = defaultdict(list)
        for item in data_items:
            grouped[item.data_type].append(item)
        return dict(grouped)
    
    def _deduplicate_data(self, data_items: List[CollectedData]) -> List[CollectedData]:
        """Remove duplicate data items based on content similarity."""
        if not data_items:
            return []
        
        unique_items = []
        seen_hashes = set()
        
        for item in data_items:
            # Create content hash for deduplication
            content_hash = self._create_content_hash(item)
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_items.append(item)
                self.deduplication_cache[content_hash].append(item.id)
            else:
                # Add to existing group for cross-referencing
                self.deduplication_cache[content_hash].append(item.id)
        
        return unique_items
    
    def _create_content_hash(self, data_item: CollectedData) -> str:
        """Create a hash for content-based deduplication."""
        # Extract key content for hashing
        content_parts = []
        
        if isinstance(data_item.data, dict):
            # Use title, description, and key fields
            key_fields = ['title', 'name', 'description', 'abstract', 'summary']
            for field in key_fields:
                if field in data_item.data and data_item.data[field]:
                    content_parts.append(str(data_item.data[field]).lower().strip())
        elif isinstance(data_item.data, str):
            content_parts.append(data_item.data.lower().strip())
        
        # Add data type and source for context
        content_parts.append(data_item.data_type)
        content_parts.append(data_item.source.name)
        
        # Create hash
        content_string = '|'.join(content_parts)
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def _merge_similar_data(self, data_items: List[CollectedData]) -> List[CollectedData]:
        """Merge similar data items to create consolidated entries."""
        if not data_items:
            return []
        
        merged_items = []
        processed_indices = set()
        
        for i, item in enumerate(data_items):
            if i in processed_indices:
                continue
            
            # Find similar items
            similar_items = [item]
            processed_indices.add(i)
            
            for j, other_item in enumerate(data_items[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                if self._are_similar(item, other_item):
                    similar_items.append(other_item)
                    processed_indices.add(j)
            
            # Merge similar items
            if len(similar_items) > 1:
                merged_item = self._merge_items(similar_items)
                merged_items.append(merged_item)
            else:
                merged_items.append(item)
        
        return merged_items
    
    def _are_similar(self, item1: CollectedData, item2: CollectedData) -> bool:
        """Check if two data items are similar enough to merge."""
        # Must be same data type
        if item1.data_type != item2.data_type:
            return False
        
        # Check title similarity
        title1 = self._extract_title(item1)
        title2 = self._extract_title(item2)
        
        if title1 and title2:
            similarity = self._calculate_text_similarity(title1, title2)
            if similarity >= self.config.similarity_threshold:
                return True
        
        # Check content similarity for text data
        if isinstance(item1.data, str) and isinstance(item2.data, str):
            similarity = self._calculate_text_similarity(item1.data, item2.data)
            if similarity >= self.config.similarity_threshold:
                return True
        
        return False
    
    def _extract_title(self, data_item: CollectedData) -> Optional[str]:
        """Extract title from data item."""
        if isinstance(data_item.data, dict):
            title_fields = ['title', 'name', 'headline']
            for field in title_fields:
                if field in data_item.data and data_item.data[field]:
                    return str(data_item.data[field])
        return None
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _merge_items(self, items: List[CollectedData]) -> CollectedData:
        """Merge multiple similar data items into one."""
        if not items:
            raise ValueError("Cannot merge empty list of items")
        
        if len(items) == 1:
            return items[0]
        
        # Use the highest quality item as base
        base_item = max(items, key=lambda x: x.relevance_score)
        
        # Merge data
        merged_data = base_item.data.copy() if isinstance(base_item.data, dict) else base_item.data
        
        if isinstance(merged_data, dict):
            # Add information from other items
            for item in items:
                if item.id == base_item.id:
                    continue
                
                if isinstance(item.data, dict):
                    for key, value in item.data.items():
                        if key not in merged_data or not merged_data[key]:
                            merged_data[key] = value
                        elif key in ['description', 'abstract', 'summary'] and value:
                            # Append additional information
                            existing = str(merged_data[key])
                            new = str(value)
                            if new not in existing:
                                merged_data[key] = f"{existing}\n\n{new}"
        
        # Create merged item
        merged_item = CollectedData(
            id=f"merged_{base_item.id}",
            data=merged_data,
            data_type=base_item.data_type,
            source=base_item.source,
            relevance_score=base_item.relevance_score,
            collected_at=base_item.collected_at,
            processing_notes=f"Merged from {len(items)} similar items: {', '.join([item.id for item in items])}",
            raw_response=base_item.raw_response
        )
        
        return merged_item
    
    def _create_aggregated_item(self, 
                              data_item: CollectedData, 
                              research_context: Optional[Dict[str, Any]] = None) -> AggregatedData:
        """Create an aggregated data item."""
        # Generate unique ID
        item_id = f"agg_{data_item.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract title and description
        title = self._extract_title(data_item) or f"{data_item.data_type} Data"
        description = self._extract_description(data_item) or f"Data from {data_item.source.name}"
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(data_item, research_context)
        
        # Find cross-references
        cross_references = self._find_cross_references(data_item)
        
        return AggregatedData(
            id=item_id,
            title=title,
            description=description,
            data_type=data_item.data_type,
            aggregated_data=data_item.data,
            source_data=[data_item],
            cross_references=cross_references,
            confidence_score=confidence_score
        )
    
    def _extract_description(self, data_item: CollectedData) -> Optional[str]:
        """Extract description from data item."""
        if isinstance(data_item.data, dict):
            desc_fields = ['description', 'abstract', 'summary', 'content']
            for field in desc_fields:
                if field in data_item.data and data_item.data[field]:
                    return str(data_item.data[field])[:500]  # Limit length
        elif isinstance(data_item.data, str):
            return data_item.data[:500]  # Limit length
        return None
    
    def _calculate_confidence_score(self, 
                                  data_item: CollectedData, 
                                  research_context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate confidence score for aggregated data."""
        score = 0.0
        
        # Base score from source reliability
        score += data_item.source.reliability_score * 0.4
        
        # Relevance score
        score += data_item.relevance_score * 0.3
        
        # Data completeness
        if isinstance(data_item.data, dict) and len(data_item.data) > 3:
            score += 0.2
        elif isinstance(data_item.data, str) and len(data_item.data) > 100:
            score += 0.2
        
        # Recency (newer data gets higher score)
        days_old = (datetime.now() - data_item.collected_at).days
        if days_old <= 1:
            score += 0.1
        elif days_old <= 7:
            score += 0.05
        
        return min(score, 1.0)
    
    def _find_cross_references(self, data_item: CollectedData) -> List[str]:
        """Find cross-references to related data."""
        cross_refs = []
        
        # Check deduplication cache for related items
        content_hash = self._create_content_hash(data_item)
        related_items = self.deduplication_cache.get(content_hash, [])
        
        for related_id in related_items:
            if related_id != data_item.id:
                cross_refs.append(related_id)
        
        return cross_refs
    
    def get_aggregated_item(self, item_id: str) -> Optional[AggregatedData]:
        """Get a specific aggregated item by ID."""
        return self.aggregated_items.get(item_id)
    
    def search_aggregated_data(self, 
                             query: str, 
                             data_type: Optional[str] = None,
                             min_confidence: float = 0.0) -> List[AggregatedData]:
        """Search aggregated data items."""
        results = []
        query_lower = query.lower()
        
        for item in self.aggregated_items.values():
            if item.confidence_score < min_confidence:
                continue
            
            if data_type and item.data_type != data_type:
                continue
            
            # Search in title and description
            if (query_lower in item.title.lower() or 
                query_lower in item.description.lower()):
                results.append(item)
                continue
            
            # Search in aggregated data
            if isinstance(item.aggregated_data, dict):
                for value in item.aggregated_data.values():
                    if isinstance(value, str) and query_lower in value.lower():
                        results.append(item)
                        break
        
        # Sort by confidence score
        results.sort(key=lambda x: x.confidence_score, reverse=True)
        return results
    
    def get_aggregation_summary(self) -> Dict[str, Any]:
        """Get summary of aggregated data."""
        if not self.aggregated_items:
            return {"total_items": 0, "data_types": {}, "sources": {}}
        
        # Count by data type
        data_types = defaultdict(int)
        sources = defaultdict(int)
        confidence_scores = []
        
        for item in self.aggregated_items.values():
            data_types[item.data_type] += 1
            for source_data in item.source_data:
                sources[source_data.source.name] += 1
            confidence_scores.append(item.confidence_score)
        
        return {
            "total_items": len(self.aggregated_items),
            "data_types": dict(data_types),
            "sources": dict(sources),
            "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
            "high_confidence_items": sum(1 for score in confidence_scores if score >= 0.8),
            "aggregated_at": datetime.now().isoformat()
        }
    
    def export_aggregated_data(self, format: str = "json") -> str:
        """Export aggregated data in specified format."""
        if format == "json":
            export_data = {
                "summary": self.get_aggregation_summary(),
                "items": []
            }
            
            for item in self.aggregated_items.values():
                item_data = {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "data_type": item.data_type,
                    "confidence_score": item.confidence_score,
                    "cross_references": item.cross_references,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat(),
                    "data": item.aggregated_data
                }
                export_data["items"].append(item_data)
            
            return json.dumps(export_data, indent=2, default=str)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
