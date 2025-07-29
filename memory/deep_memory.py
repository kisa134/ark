#!/usr/bin/env python3
"""
ARK v2.8 - Deep Memory System
Knowledge Graph and long-term memory management
"""

import sqlite3
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

import networkx as nx
from collections import defaultdict


class MemoryType(Enum):
    """Types of memory"""
    REASONING = "reasoning"
    EMOTION = "emotion"
    SELF_PATCH = "self_patch"
    HOMEOSTASIS = "homeostasis"
    INSIGHT = "insight"
    PATTERN = "pattern"
    GOAL = "goal"
    EXPERIENCE = "experience"


class MemoryPriority(Enum):
    """Memory priority levels"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


@dataclass
class MemoryEntry:
    """Memory entry structure"""
    id: Optional[int]
    timestamp: float
    memory_type: MemoryType
    content: Dict[str, Any]
    priority: MemoryPriority
    associations: List[str]
    emotional_trace: Dict[str, float]
    consciousness_state: str
    attention_level: float
    reasoning_depth: int
    tags: List[str]
    access_count: int
    last_accessed: float
    decay_rate: float


class KnowledgeGraph:
    """Knowledge Graph for memory associations"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.logger = logging.getLogger(__name__)
        
    def add_node(self, node_id: str, node_type: str, attributes: Dict[str, Any]):
        """Add node to knowledge graph"""
        self.graph.add_node(node_id, type=node_type, **attributes)
        
    def add_edge(self, node1: str, node2: str, relationship: str, weight: float = 1.0):
        """Add edge between nodes"""
        self.graph.add_edge(node1, node2, relationship=relationship, weight=weight)
        
    def find_associations(self, node_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Find associations for a node"""
        associations = []
        
        if node_id in self.graph:
            # Find nodes within max_depth
            for target_node in nx.single_source_shortest_path_length(self.graph, node_id, cutoff=max_depth):
                if target_node != node_id:
                    path = nx.shortest_path(self.graph, node_id, target_node)
                    edge_data = self.graph.get_edge_data(path[0], path[1])
                    
                    associations.append({
                        "node": target_node,
                        "relationship": edge_data.get("relationship", "related"),
                        "weight": edge_data.get("weight", 1.0),
                        "path_length": len(path) - 1
                    })
        
        return sorted(associations, key=lambda x: x["weight"], reverse=True)
    
    def find_patterns(self, memory_type: MemoryType, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """Find patterns in memory"""
        patterns = []
        
        # Get all nodes of the specified type
        type_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get("type") == memory_type.value]
        
        # Analyze connections between nodes
        for node in type_nodes:
            neighbors = list(self.graph.neighbors(node))
            if len(neighbors) >= min_occurrences:
                pattern = {
                    "central_node": node,
                    "connections": len(neighbors),
                    "neighbors": neighbors[:10],  # Limit to first 10
                    "strength": sum(self.graph[node][n]["weight"] for n in neighbors)
                }
                patterns.append(pattern)
        
        return sorted(patterns, key=lambda x: x["strength"], reverse=True)


class DeepMemorySystem:
    """Deep memory system with Knowledge Graph"""
    
    def __init__(self, db_path: str = "data/ark_memory.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.knowledge_graph = KnowledgeGraph()
        
        # Create database and tables
        self._init_database()
        
        # Memory caches
        self.short_term_cache: List[MemoryEntry] = []
        self.long_term_cache: Dict[int, MemoryEntry] = {}
        
        # Memory limits
        self.short_term_limit = 100
        self.long_term_limit = 10000
        
        self.logger.info("Deep Memory System initialized")
    
    def _init_database(self):
        """Initialize database tables"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    associations TEXT NOT NULL,
                    emotional_trace TEXT NOT NULL,
                    consciousness_state TEXT NOT NULL,
                    attention_level REAL NOT NULL,
                    reasoning_depth INTEGER NOT NULL,
                    tags TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL NOT NULL,
                    decay_rate REAL DEFAULT 0.1
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_entries(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON memory_entries(priority)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON memory_entries(tags)")
            
            conn.commit()
    
    def store_memory(self, memory_type: MemoryType, content: Dict[str, Any], 
                    priority: MemoryPriority = MemoryPriority.MEDIUM,
                    associations: List[str] = None,
                    emotional_trace: Dict[str, float] = None,
                    consciousness_state: str = "normal",
                    attention_level: float = 0.5,
                    reasoning_depth: int = 1,
                    tags: List[str] = None) -> int:
        """Store new memory entry"""
        try:
            timestamp = time.time()
            
            # Create memory entry
            entry = MemoryEntry(
                id=None,
                timestamp=timestamp,
                memory_type=memory_type,
                content=content,
                priority=priority,
                associations=associations or [],
                emotional_trace=emotional_trace or {},
                consciousness_state=consciousness_state,
                attention_level=attention_level,
                reasoning_depth=reasoning_depth,
                tags=tags or [],
                access_count=0,
                last_accessed=timestamp,
                decay_rate=0.1
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO memory_entries (
                        timestamp, memory_type, content, priority, associations,
                        emotional_trace, consciousness_state, attention_level,
                        reasoning_depth, tags, access_count, last_accessed, decay_rate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.timestamp,
                    entry.memory_type.value,
                    json.dumps(entry.content),
                    entry.priority.value,
                    json.dumps(entry.associations),
                    json.dumps(entry.emotional_trace),
                    entry.consciousness_state,
                    entry.attention_level,
                    entry.reasoning_depth,
                    json.dumps(entry.tags),
                    entry.access_count,
                    entry.last_accessed,
                    entry.decay_rate
                ))
                
                entry.id = cursor.lastrowid
                conn.commit()
            
            # Add to Knowledge Graph
            self._add_to_knowledge_graph(entry)
            
            # Add to short-term cache
            self.short_term_cache.append(entry)
            if len(self.short_term_cache) > self.short_term_limit:
                self._cleanup_short_term_cache()
            
            self.logger.info(f"Stored memory: {memory_type.value} (ID: {entry.id})")
            return entry.id
            
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")
            return -1
    
    def _add_to_knowledge_graph(self, entry: MemoryEntry):
        """Add memory entry to knowledge graph"""
        try:
            node_id = f"{entry.memory_type.value}_{entry.id}"
            
            # Add node
            self.knowledge_graph.add_node(node_id, entry.memory_type.value, {
                "content": entry.content,
                "priority": entry.priority.value,
                "consciousness_state": entry.consciousness_state,
                "attention_level": entry.attention_level,
                "reasoning_depth": entry.reasoning_depth,
                "tags": entry.tags
            })
            
            # Add edges for associations
            for assoc in entry.associations:
                if assoc in self.knowledge_graph.graph:
                    self.knowledge_graph.add_edge(node_id, assoc, "associated", 1.0)
            
            # Add edges for tags
            for tag in entry.tags:
                tag_node = f"tag_{tag}"
                if tag_node not in self.knowledge_graph.graph:
                    self.knowledge_graph.add_node(tag_node, "tag", {"name": tag})
                self.knowledge_graph.add_edge(node_id, tag_node, "tagged", 0.5)
                
        except Exception as e:
            self.logger.error(f"Failed to add to knowledge graph: {e}")
    
    def retrieve_memory(self, memory_id: int) -> Optional[MemoryEntry]:
        """Retrieve memory by ID"""
        try:
            # Check cache first
            if memory_id in self.long_term_cache:
                entry = self.long_term_cache[memory_id]
                entry.access_count += 1
                entry.last_accessed = time.time()
                return entry
            
            # Retrieve from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM memory_entries WHERE id = ?", (memory_id,))
                row = cursor.fetchone()
                
                if row:
                    entry = self._row_to_memory_entry(row)
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                    
                    # Update access count in database
                    cursor.execute("UPDATE memory_entries SET access_count = ?, last_accessed = ? WHERE id = ?",
                                 (entry.access_count, entry.last_accessed, memory_id))
                    conn.commit()
                    
                    # Add to cache
                    self.long_term_cache[memory_id] = entry
                    
                    return entry
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve memory {memory_id}: {e}")
        
        return None
    
    def _row_to_memory_entry(self, row: Tuple) -> MemoryEntry:
        """Convert database row to MemoryEntry"""
        return MemoryEntry(
            id=row[0],
            timestamp=row[1],
            memory_type=MemoryType(row[2]),
            content=json.loads(row[3]),
            priority=MemoryPriority(row[4]),
            associations=json.loads(row[5]),
            emotional_trace=json.loads(row[6]),
            consciousness_state=row[7],
            attention_level=row[8],
            reasoning_depth=row[9],
            tags=json.loads(row[10]),
            access_count=row[11],
            last_accessed=row[12],
            decay_rate=row[13]
        )
    
    def search_memories(self, query: str = None, memory_type: MemoryType = None,
                       tags: List[str] = None, limit: int = 50) -> List[MemoryEntry]:
        """Search memories by various criteria"""
        try:
            conditions = []
            params = []
            
            if query:
                conditions.append("content LIKE ?")
                params.append(f"%{query}%")
            
            if memory_type:
                conditions.append("memory_type = ?")
                params.append(memory_type.value)
            
            if tags:
                for tag in tags:
                    conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT * FROM memory_entries 
                    WHERE {where_clause}
                    ORDER BY priority DESC, last_accessed DESC
                    LIMIT ?
                """, params + [limit])
                
                rows = cursor.fetchall()
                return [self._row_to_memory_entry(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []
    
    def get_recent_memories(self, hours: int = 24, memory_type: MemoryType = None) -> List[MemoryEntry]:
        """Get recent memories"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if memory_type:
                    cursor.execute("""
                        SELECT * FROM memory_entries 
                        WHERE timestamp > ? AND memory_type = ?
                        ORDER BY timestamp DESC
                    """, (cutoff_time, memory_type.value))
                else:
                    cursor.execute("""
                        SELECT * FROM memory_entries 
                        WHERE timestamp > ?
                        ORDER BY timestamp DESC
                    """, (cutoff_time,))
                
                rows = cursor.fetchall()
                return [self._row_to_memory_entry(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get recent memories: {e}")
            return []
    
    def get_memory_patterns(self, memory_type: MemoryType = None) -> List[Dict[str, Any]]:
        """Get memory patterns from Knowledge Graph"""
        try:
            if memory_type:
                return self.knowledge_graph.find_patterns(memory_type)
            else:
                patterns = []
                for mem_type in MemoryType:
                    patterns.extend(self.knowledge_graph.find_patterns(mem_type))
                return patterns
                
        except Exception as e:
            self.logger.error(f"Failed to get memory patterns: {e}")
            return []
    
    def get_memory_associations(self, memory_id: int) -> List[Dict[str, Any]]:
        """Get associations for a memory"""
        try:
            node_id = f"memory_{memory_id}"
            return self.knowledge_graph.find_associations(node_id)
        except Exception as e:
            self.logger.error(f"Failed to get memory associations: {e}")
            return []
    
    def _cleanup_short_term_cache(self):
        """Clean up short-term cache"""
        # Remove oldest entries
        self.short_term_cache.sort(key=lambda x: x.timestamp)
        self.short_term_cache = self.short_term_cache[-self.short_term_limit//2:]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total memories
                cursor.execute("SELECT COUNT(*) FROM memory_entries")
                total_memories = cursor.fetchone()[0]
                
                # Memories by type
                cursor.execute("SELECT memory_type, COUNT(*) FROM memory_entries GROUP BY memory_type")
                memories_by_type = dict(cursor.fetchall())
                
                # Average access count
                cursor.execute("SELECT AVG(access_count) FROM memory_entries")
                avg_access = cursor.fetchone()[0] or 0
                
                # Recent activity
                recent_cutoff = time.time() - 3600  # Last hour
                cursor.execute("SELECT COUNT(*) FROM memory_entries WHERE timestamp > ?", (recent_cutoff,))
                recent_memories = cursor.fetchone()[0]
                
                return {
                    "total_memories": total_memories,
                    "memories_by_type": memories_by_type,
                    "average_access_count": avg_access,
                    "recent_memories": recent_memories,
                    "short_term_cache_size": len(self.short_term_cache),
                    "long_term_cache_size": len(self.long_term_cache),
                    "knowledge_graph_nodes": self.knowledge_graph.graph.number_of_nodes(),
                    "knowledge_graph_edges": self.knowledge_graph.graph.number_of_edges()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {}


# Global memory system instance
deep_memory = DeepMemorySystem() 