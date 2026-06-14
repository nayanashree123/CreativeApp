"""
Tests for CreativeApp UI Components

Phase 7: Gradio UI Testing
Validates all UI components and integration with orchestrator
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.app import CreativeAppUI
from src.core.models import DreamProfile


async def test_ui_initialization():
    """Test UI controller initialization"""
    print("\n🧪 Test 1: UI Initialization")
    try:
        ui = CreativeAppUI()
        assert ui.orchestrator is not None, "Orchestrator not initialized"
        assert ui.last_result is None, "Last result should be None initially"
        assert len(ui.analysis_history) == 0, "History should be empty"
        print("✅ UI initialization successful")
        return True
    except Exception as e:
        print(f"❌ UI initialization failed: {e}")
        return False


async def test_decision_card_generation():
    """Test decision card HTML generation"""
    print("\n🧪 Test 2: Decision Card Generation")
    try:
        ui = CreativeAppUI()
        
        # Analyze a simple dream
        result = await ui.analyze_dream(
            dream_text="AI-powered customer support chatbot",
            idea_name="ChatSupport Pro"
        )
        
        decision_html, _, _, _, status = result
        
        # Validate output
        assert "Decision" in decision_html or "error" not in decision_html.lower(), "No decision output"
        assert len(decision_html) > 50, "Decision card too short"
        
        print(f"✅ Decision card generated ({len(decision_html)} chars)")
        return True
    except Exception as e:
        print(f"❌ Decision card generation failed: {e}")
        return False


async def test_radar_chart_generation():
    """Test radar chart generation"""
    print("\n🧪 Test 3: Radar Chart Generation")
    try:
        ui = CreativeAppUI()
        
        # Analyze dream
        result = await ui.analyze_dream(
            dream_text="Vertical SaaS for real estate",
            idea_name="PropTech"
        )
        
        _, radar_html, _, _, _ = result
        
        # Validate
        assert len(radar_html) > 100, "Radar chart too short"
        assert "plotly" in radar_html.lower() or "scatterpolar" in radar_html.lower(), "No plotly chart"
        
        print(f"✅ Radar chart generated ({len(radar_html)} chars)")
        return True
    except Exception as e:
        print(f"❌ Radar chart generation failed: {e}")
        return False


async def test_agent_table_generation():
    """Test agent voting table generation"""
    print("\n🧪 Test 4: Agent Table Generation")
    try:
        ui = CreativeAppUI()
        
        # Analyze
        result = await ui.analyze_dream(
            dream_text="Mobile marketplace app",
            idea_name="MobileMarket"
        )
        
        _, _, agent_table, _, _ = result
        
        # Validate table
        assert "<table" in agent_table or "<tr" in agent_table, "No table structure"
        assert "Agent" in agent_table, "No agent names"
        assert "Confidence" in agent_table, "No confidence scores"
        
        print(f"✅ Agent table generated ({len(agent_table)} chars)")
        return True
    except Exception as e:
        print(f"❌ Agent table generation failed: {e}")
        return False


async def test_roadmap_generation():
    """Test roadmap timeline generation"""
    print("\n🧪 Test 5: Roadmap Generation")
    try:
        ui = CreativeAppUI()
        
        # Analyze
        result = await ui.analyze_dream(
            dream_text="API-first development platform",
            idea_name="DevAPI"
        )
        
        _, _, _, roadmap_html, _ = result
        
        # Validate
        assert len(roadmap_html) > 50, "Roadmap too short"
        assert "Month" in roadmap_html or "Phase" in roadmap_html or "roadmap" in roadmap_html.lower(), "No timeline"
        
        print(f"✅ Roadmap generated ({len(roadmap_html)} chars)")
        return True
    except Exception as e:
        print(f"❌ Roadmap generation failed: {e}")
        return False


async def test_analysis_history():
    """Test analysis history tracking"""
    print("\n🧪 Test 6: Analysis History")
    try:
        ui = CreativeAppUI()
        
        # Run multiple analyses
        ideas = [
            ("AI chatbot", "ChatBot"),
            ("Mobile app", "MobileApp"),
            ("SaaS platform", "SaaS")
        ]
        
        for dream, name in ideas:
            await ui.analyze_dream(dream, name)
        
        # Validate history
        assert len(ui.analysis_history) == 3, f"Expected 3 analyses, got {len(ui.analysis_history)}"
        assert ui.analysis_history[0]["idea_name"] == "ChatBot", "Wrong first idea"
        assert all("timestamp" in h for h in ui.analysis_history), "Missing timestamps"
        
        print(f"✅ History tracking works ({len(ui.analysis_history)} analyses)")
        return True
    except Exception as e:
        print(f"❌ History tracking failed: {e}")
        return False


async def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\n🧪 Test 7: Error Handling")
    try:
        ui = CreativeAppUI()
        
        # Test with empty input
        result = await ui.analyze_dream("", "Empty Dream")
        decision, _, _, _, status = result
        
        assert "Error" in decision or "error" in decision.lower(), "Should handle empty input"
        
        # Test with valid input after error
        result = await ui.analyze_dream("Valid idea", "ValidDream")
        decision, _, _, _, status = result
        
        assert "Error" not in decision or "✅" in status, "Should recover from error"
        
        print("✅ Error handling works correctly")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def test_json_export():
    """Test JSON export functionality"""
    print("\n🧪 Test 8: JSON Export")
    try:
        ui = CreativeAppUI()
        
        # Analyze
        await ui.analyze_dream("AI idea", "TestIdea")
        
        # Export
        json_str = ui.export_analysis_json()
        
        # Validate
        assert "{" in json_str, "No JSON output"
        assert "final_decision" in json_str or "decision" in json_str.lower(), "Missing decision field"
        
        print(f"✅ JSON export works ({len(json_str)} chars)")
        return True
    except Exception as e:
        print(f"❌ JSON export failed: {e}")
        return False


async def main():
    """Run all UI tests"""
    print("\n" + "="*60)
    print("🎨 CREATIVEAPP UI TESTING - PHASE 7")
    print("="*60)
    
    tests = [
        test_ui_initialization,
        test_decision_card_generation,
        test_radar_chart_generation,
        test_agent_table_generation,
        test_roadmap_generation,
        test_analysis_history,
        test_error_handling,
        test_json_export,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test error: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed}/{total} PASSING")
    print("="*60)
    
    if passed == total:
        print("\n✅ ALL UI TESTS PASSED! UI is ready for deployment.")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please review.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
