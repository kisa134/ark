#!/usr/bin/env python3
"""
Test Brain Trust - Distributed Cognitive Architecture
Tests the new brain departments system
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

from mind.brain_departments import brain_trust, BrainDepartment, BrainConsensus


async def test_brain_departments():
    """Test individual brain departments"""
    print("🧠 Testing Brain Departments...")
    
    test_inputs = [
        "Analyze system performance and identify bottlenecks",
        "Design a new feature for user authentication",
        "Review the current codebase for security vulnerabilities",
        "Document the evolution process and create user guide",
        "Optimize memory usage in the main application"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n📝 Test {i}: {test_input}")
        
        try:
            # Test individual departments
            for dept in BrainDepartment:
                if dept in brain_trust.departments:
                    agent = brain_trust.departments[dept]
                    result = await agent.process_input(test_input, {"test": True})
                    
                    print(f"  [{dept.value.upper()}] Confidence: {result.confidence:.2f}")
                    print(f"       Output: {result.output[:100]}...")
                    
                    if result.confidence < 0.5:
                        print(f"       ⚠️  Low confidence detected")
        
        except Exception as e:
            print(f"  ❌ Error testing {test_input}: {e}")


async def test_brain_pipeline():
    """Test the complete brain pipeline"""
    print("\n🔄 Testing Brain Pipeline...")
    
    test_cases = [
        {
            "input": "Implement a new self-improvement algorithm",
            "context": {"priority": "high", "domain": "evolution"}
        },
        {
            "input": "Analyze and fix the current performance issues",
            "context": {"priority": "medium", "domain": "optimization"}
        },
        {
            "input": "Design a new user interface for the monitoring dashboard",
            "context": {"priority": "low", "domain": "ui"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 Test Case {i}: {test_case['input']}")
        
        try:
            start_time = time.time()
            consensus = await brain_trust.process_through_pipeline(
                test_case["input"], 
                test_case["context"]
            )
            end_time = time.time()
            
            print(f"  ⏱️  Processing time: {end_time - start_time:.2f}s")
            print(f"  🎯 Confidence: {consensus.confidence_score:.2f}")
            print(f"  📊 Departments involved: {len(consensus.department_votes)}")
            print(f"  🔍 Conflicts detected: {len(consensus.conflicts)}")
            
            if consensus.conflicts:
                print(f"  ⚠️  Conflicts: {consensus.conflicts}")
            
            print(f"  💡 Final Decision: {consensus.final_decision[:200]}...")
            print(f"  🧠 Meta Analysis: {consensus.meta_analysis[:200]}...")
            
            # Show department outputs
            print("  📋 Department Outputs:")
            for dept, output in consensus.department_votes.items():
                print(f"    [{dept.value}]: {output[:100]}...")
        
        except Exception as e:
            print(f"  ❌ Error in pipeline test: {e}")


async def test_brain_evolution():
    """Test brain evolution capabilities"""
    print("\n🚀 Testing Brain Evolution...")
    
    evolution_tasks = [
        "Evolve the system to handle higher load",
        "Improve the reasoning capabilities",
        "Optimize the memory management system",
        "Enhance the security features"
    ]
    
    for i, task in enumerate(evolution_tasks, 1):
        print(f"\n🔄 Evolution Task {i}: {task}")
        
        try:
            consensus = await brain_trust.process_through_pipeline(task, {
                "evolution_type": "self_improvement",
                "priority": "high"
            })
            
            print(f"  🎯 Evolution confidence: {consensus.confidence_score:.2f}")
            
            if consensus.confidence_score > 0.7:
                print(f"  ✅ High confidence evolution - ready to apply")
            elif consensus.confidence_score > 0.5:
                print(f"  ⚠️  Medium confidence - needs review")
            else:
                print(f"  ❌ Low confidence - evolution blocked")
            
            print(f"  💡 Evolution plan: {consensus.final_decision[:200]}...")
            
        except Exception as e:
            print(f"  ❌ Error in evolution test: {e}")


def test_brain_status():
    """Test brain status reporting"""
    print("\n📊 Testing Brain Status...")
    
    try:
        status = brain_trust.get_department_status()
        print(f"  📈 Active departments: {len(status)}")
        
        for dept_name, dept_status in status.items():
            print(f"    [{dept_name}]")
            print(f"      Model: {dept_status.get('model', 'unknown')}")
            print(f"      Memory: {dept_status.get('memory_size', 0)} entries")
            print(f"      Tools: {dept_status.get('tools_count', 0)}")
            print(f"      Status: {dept_status.get('status', 'unknown')}")
        
        history = brain_trust.get_consensus_history()
        print(f"  📚 Consensus history: {len(history)} decisions")
        
        if history:
            latest = history[-1]
            print(f"  🕒 Latest decision: {latest.get('timestamp', 'unknown')}")
            print(f"  🎯 Latest confidence: {latest.get('confidence', 0):.2f}")
        
    except Exception as e:
        print(f"  ❌ Error getting brain status: {e}")


async def main():
    """Main test function"""
    print("🧠 ARK Brain Trust Test Suite")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Test individual departments
        await test_brain_departments()
        
        # Test complete pipeline
        await test_brain_pipeline()
        
        # Test evolution capabilities
        await test_brain_evolution()
        
        # Test status reporting
        test_brain_status()
        
        print("\n✅ Brain Trust tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 