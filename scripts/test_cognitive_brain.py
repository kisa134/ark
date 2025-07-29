#!/usr/bin/env python3
"""
Test Cognitive Brain - Full cognitive architecture testing
Tests the complete cognitive brain with all departments and components
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from mind.cognitive_architecture import (
    cognitive_brain, PerceptionLayer, AttentionScheduler, 
    WorkingMemory, BrainTrust, EmotionEngine, Dispatcher,
    CognitiveEventType, CognitiveEvent
)


async def test_perception_layer():
    """Test perception layer"""
    print("🔍 Testing Perception Layer...")
    
    perception = PerceptionLayer()
    
    test_inputs = [
        ("user_chat", "Hello, how are you?", "user"),
        ("hardware_monitor", {"cpu": 85, "memory": 70}, "hardware"),
        ("system_update", {"version": "2.8.1", "changes": ["bug_fix"]}, "system")
    ]
    
    for i, (input_type, data, source) in enumerate(test_inputs, 1):
        print(f"  📝 Test {i}: {input_type}")
        
        if input_type == "user_chat":
            event = perception.process_input(data, source)
        elif input_type == "hardware_monitor":
            event = perception.process_hardware_alert(data)
        elif input_type == "system_update":
            event = perception.process_system_update(data)
        
        print(f"    Event type: {event.event_type.value}")
        print(f"    Priority: {event.priority}")
        print(f"    Timestamp: {event.timestamp}")
        print(f"    ✅ Event processed successfully")


async def test_attention_scheduler():
    """Test attention scheduler"""
    print("\n🎯 Testing Attention Scheduler...")
    
    attention = AttentionScheduler()
    
    test_events = [
        CognitiveEvent(
            event_type=CognitiveEventType.USER_INPUT,
            data={"text": "Hello"},
            priority=2,
            timestamp=datetime.now(),
            source="user"
        ),
        CognitiveEvent(
            event_type=CognitiveEventType.HARDWARE_ALERT,
            data={"cpu": 95},
            priority=1,
            timestamp=datetime.now(),
            source="hardware"
        ),
        CognitiveEvent(
            event_type=CognitiveEventType.SYSTEM_UPDATE,
            data={"version": "2.8.1"},
            priority=3,
            timestamp=datetime.now(),
            source="system"
        )
    ]
    
    for i, event in enumerate(test_events, 1):
        print(f"  📝 Processing event {i}: {event.event_type.value}")
        
        focus = attention.process_event(event)
        
        print(f"    Focus topic: {focus.topic}")
        print(f"    Priority: {focus.priority}")
        print(f"    Reasoning chain: {len(focus.reasoning_chain)} steps")
        print(f"    Current focus: {focus.topic}")
        print(f"    Background tasks: {len(focus.background_tasks)}")


async def test_working_memory():
    """Test working memory"""
    print("\n🧠 Testing Working Memory...")
    
    memory = WorkingMemory()
    
    test_items = [
        ("user_request", "Optimize system performance"),
        ("hardware_status", {"cpu": 85, "memory": 70}),
        ("reasoning_result", {"confidence": 0.8, "solution": "Apply optimizations"}),
        ("emotion_state", {"joy": 0.6, "trust": 0.7}),
        ("context", {"session_id": "test_123", "user_id": "user"})
    ]
    
    for key, value in test_items:
        memory.store(key, value)
        print(f"  💾 Stored: {key} -> {str(value)[:50]}...")
    
    print("  📖 Retrieving items:")
    for key, _ in test_items:
        value = memory.retrieve(key)
        print(f"    {key}: {str(value)[:50]}...")
    
    context = memory.retrieve_context(["user_request", "hardware_status"])
    print(f"  🔗 Context: {len(context)} items retrieved")


async def test_brain_departments():
    """Test brain departments"""
    print("\n🏢 Testing Reasoning Departments...")
    
    brain_trust = BrainTrust()
    
    test_input = "Implement a new optimization algorithm"
    context = {"priority": "high", "domain": "performance"}
    
    for dept_name, dept in brain_trust.departments.items():
        print(f"  🏛️  Testing {dept.config.name}...")
        
        try:
            result = await dept.process_input(test_input, context)
            
            print(f"    Status: ✅ Success")
            print(f"    Output: {result.output[:100]}...")
            print(f"    Confidence: {result.confidence:.2f}")
            print(f"    Model: {dept.config.model_name}")
            print(f"    Memory size: {len(dept.memory)}")
            
        except Exception as e:
            print(f"    Status: ❌ Error - {e}")


async def test_emotion_engine():
    """Test emotion engine"""
    print("\n😊 Testing Emotion Engine...")
    
    emotion_engine = EmotionEngine()
    
    test_events = [
        CognitiveEvent(
            event_type=CognitiveEventType.SYSTEM_UPDATE,
            data={"status": "success", "optimization": "applied"},
            priority=3,
            timestamp=datetime.now(),
            source="system"
        ),
        CognitiveEvent(
            event_type=CognitiveEventType.HARDWARE_ALERT,
            data={"error": "failed", "reason": "insufficient resources"},
            priority=1,
            timestamp=datetime.now(),
            source="hardware"
        ),
        CognitiveEvent(
            event_type=CognitiveEventType.USER_INPUT,
            data={"security": "vulnerability_detected", "action": "patch_applied"},
            priority=2,
            timestamp=datetime.now(),
            source="user"
        ),
        CognitiveEvent(
            event_type=CognitiveEventType.SYSTEM_UPDATE,
            data={"performance": "improved", "metrics": "better"},
            priority=3,
            timestamp=datetime.now(),
            source="system"
        )
    ]
    
    for i, event in enumerate(test_events, 1):
        print(f"  📝 Test {i}: {event.data}")
        
        response = emotion_engine.process_event(event)
        
        print(f"    Dominant emotion: {emotion_engine.get_dominant_emotion()}")
        print(f"    Emotional stability: {emotion_engine._calculate_stability():.2f}")
        print(f"    Recent triggers: {len(emotion_engine.recent_triggers)}")


async def test_dispatcher():
    """Test dispatcher functionality"""
    print("\n🚦 Testing Dispatcher...")
    
    dispatcher = Dispatcher()
    
    # Schedule test tasks
    test_tasks = [
        {"type": "optimization", "priority": 1},
        {"type": "security_check", "priority": 2},
        {"type": "documentation", "priority": 3}
    ]
    
    for task in test_tasks:
        task_id = dispatcher.schedule_reasoning(task, task["priority"])
        print(f"  📋 Scheduled: {task['type']} (priority {task['priority']})")
    
    # Get next task
    next_task = dispatcher.get_next_task()
    if next_task:
        print(f"  📥 Next task: {next_task.task_data['type']} (priority {next_task.priority})")
        
        # Complete task
        dispatcher.complete_task("task_123", {"status": "completed", "result": "success"})
        print(f"  ✅ Task completed")
    
    status = dispatcher.get_dispatcher_status()
    print(f"  📊 Queue size: {status['queue_size']}")
    print(f"  📊 Active tasks: {status['active_tasks']}")
    print(f"  📊 Completed tasks: {status['completed_tasks']}")


async def test_cognitive_brain():
    """Test complete cognitive brain"""
    print("\n🧠 Testing Complete Cognitive Brain...")
    
    test_inputs = [
        "Optimize system performance",
        "Implement new security feature",
        "Analyze current bottlenecks"
    ]
    
    for i, input_data in enumerate(test_inputs, 1):
        print(f"  📝 Test {i}: {input_data}")
        
        try:
            result = await cognitive_brain.process_input(input_data, {"test": True})
            
            if result["success"]:
                consensus = result["consensus"]
                print(f"    ✅ Success")
                print(f"    Confidence: {consensus.confidence_score:.2f}")
                print(f"    Decision: {consensus.final_decision[:100]}...")
                print(f"    Departments: {len(consensus.department_votes)}")
                print(f"    Conflicts: {len(consensus.conflicts)}")
            else:
                print(f"    ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")


async def test_brain_status():
    """Test brain status reporting"""
    print("\n📊 Testing Brain Status...")
    
    try:
        status = cognitive_brain.get_brain_status()
        
        print(f"  🧠 Perception: {status['perception']}")
        print(f"  🎯 Attention focus: {status['attention']['current_focus']}")
        print(f"  💾 Working memory items: {status['working_memory']['total_items']}")
        print(f"  🏢 Brain departments: {len(status['brain_trust'])}")
        print(f"  😊 Dominant emotion: {status['emotion_engine']['dominant_emotion']}")
        print(f"  🚦 Dispatcher queue: {status['dispatcher']['queue_size']}")
        
    except Exception as e:
        print(f"  ❌ Error getting brain status: {e}")


async def main():
    """Main test function"""
    print("🧠 ARK Cognitive Brain Test Suite")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Test individual components
        await test_perception_layer()
        await test_attention_scheduler()
        await test_working_memory()
        await test_brain_departments()
        await test_emotion_engine()
        await test_dispatcher()
        
        # Test complete cognitive brain
        await test_cognitive_brain()
        await test_brain_status()
        
        print("\n✅ Cognitive Brain tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 