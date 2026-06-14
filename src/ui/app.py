"""
CreativeApp: AI-Powered Dream Analysis Interface

Provides interactive web interface for dream/business idea analysis
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import gradio as gr
import asyncio
import json
import markdown
from typing import Dict, Any, List, Tuple
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

from src.orchestration.orchestrator import DreamAnalysisOrchestrator
from src.core.models import (
    DreamProfile,
    DreamAnalysisResult,
    DecisionType,
    FallbackAgentOutput
)
from src.utils.llm_client import initialize_llm_client


class CreativeAppUI:
    """Main UI controller for CreativeApp"""
    
    def __init__(self):
        """Initialize orchestrator and components"""
        self.orchestrator = DreamAnalysisOrchestrator(use_rag=True)
        self.last_result: DreamAnalysisResult = None
        self.analysis_history: List[Dict] = []
        self.base_feasibility: float = 0.5  # Track base feasibility for adjustments
        
    async def analyze_dream(
        self,
        dream_text: str,
        idea_name: str,
        target_market: str = "",
        budget_range: str = "$50K-$100K",
        timeline: str = "6 months"
    ) -> Tuple[str, Any, str, str, str]:  # radar_html is now a plotly figure
        """Analyze dream and return all UI components"""
        
        if not dream_text.strip():
            return (
                "❌ Error",
                go.Figure(),  # Empty figure
                "⚠️ Invalid Input",
                "No analysis available",
                "No agents analyzed"
            )
        
        try:
            # Create dream profile
            dream = DreamProfile(
                dream_text=dream_text,
                idea_name=idea_name or "Unnamed Idea",
                target_market=target_market or "General",
                budget_range=budget_range,
                timeline=timeline
            )
            
            # Analyze with orchestrator
            self.last_result = await self.orchestrator.analyze(
                dream_text=dream_text,
                idea_name=dream.idea_name,
                target_market=dream.target_market,
                budget_range=dream.budget_range,
                timeline=dream.timeline
            )
            
            # Store in history
            self.analysis_history.append({
                "timestamp": datetime.now().isoformat(),
                "idea_name": dream.idea_name,
                "decision": self.last_result.final_decision.recommendation
            })
            
            # Store base feasibility for what-if calculations
            self.base_feasibility = self.last_result.overall_feasibility
            
            # Build UI components
            decision_html = self._build_decision_card()
            radar_fig = self._build_radar_chart()  # Now returns plotly figure
            agent_table_html = self._build_agent_table()
            roadmap_html = self._build_roadmap_timeline()
            
            return (
                decision_html,
                radar_fig,
                agent_table_html,
                roadmap_html,
                "✅ Analysis Complete"
            )
            
        except Exception as e:
            import traceback
            error_msg = f"❌ Analysis Failed: {str(e)}"
            traceback.print_exc()
            return (
                error_msg,
                go.Figure(),  # Empty figure for radar chart
                error_msg,
                "No timeline generated",
                f"Error: {str(e)}"
            )
    
    def _build_decision_card(self) -> str:
        """Build the main decision recommendation card with markdown formatting"""
        if not self.last_result:
            return "<div class='card' style='font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>No analysis available</div>"
        
        result = self.last_result
        decision = result.final_decision
        
        # Handle FallbackAgentOutput
        if isinstance(decision, FallbackAgentOutput):
            return f"<div style='background: #fef2f2; color: #991b1b; padding: 16px; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>Decision analysis failed: {decision.error.error_message}</div>"
        
        # Color coding based on decision
        color_map = {
            DecisionType.PURSUE: "#10b981",      # Green
            DecisionType.PIVOT: "#f59e0b",       # Amber
            DecisionType.DELAY: "#3b82f6",       # Blue
            DecisionType.REJECT: "#ef4444"       # Red
        }
        
        color = color_map.get(decision.recommendation, "#6b7280")
        
        # Format key actions as markdown bullet list
        actions_md = "\n".join([f"- {action}" for action in decision.key_actions]) if decision.key_actions else "No specific actions identified"
        actions_html = markdown.markdown(actions_md, extensions=['extra'])
        
        # Format reasoning as markdown (in case it has code blocks or formatting)
        reasoning_html = markdown.markdown(decision.reasoning, extensions=['extra'])
        
        html = f"""
        <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
                    border: 2px solid {color};
                    border-radius: 12px;
                    padding: 24px;
                    margin: 16px 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0; color: {color}; font-size: 28px; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    {decision.recommendation}
                </h2>
                <div style="font-size: 48px;">
                    {'🚀' if decision.recommendation == DecisionType.PURSUE else 
                     '🔄' if decision.recommendation == DecisionType.PIVOT else 
                     '⏸️' if decision.recommendation == DecisionType.DELAY else 
                     '❌'}
                </div>
            </div>
            
            <div style="margin: 16px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                <p style="margin: 8px 0; font-size: 16px; font-weight: 500;"><strong>Confidence:</strong> {decision.confidence*100:.0f}%</p>
                <p style="margin: 8px 0; font-size: 16px; font-weight: 500;"><strong>Feasibility:</strong> {result.overall_feasibility*100:.0f}%</p>
            </div>
            
            <div style="background: white; border-radius: 8px; padding: 16px; margin-top: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                <p style="margin: 0 0 12px 0; font-size: 14px; font-weight: 600; color: #1f2937; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    <strong>Reasoning:</strong>
                </p>
                <div style="color: #374151; line-height: 1.6; font-size: 14px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    {reasoning_html}
                </div>
            </div>
            
            <div style="background: white; border-radius: 8px; padding: 16px; margin-top: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                <p style="margin: 0 0 12px 0; font-size: 14px; font-weight: 600; color: #1f2937; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    <strong>📋 Key Actions:</strong>
                </p>
                <div style="color: #374151; line-height: 1.8; font-size: 14px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    {actions_html}
                </div>
            </div>
            
            <div style="background: #f0f9ff; border-left: 4px solid {color}; padding: 16px; border-radius: 4px; margin-top: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0; color: {color}; font-size: 14px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">Decision Factors</h4>
                <ul style="margin: 0; padding-left: 20px; color: #374151; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    {''.join([f"<li style='margin-bottom: 6px; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>{factor}</li>" for factor in decision.key_decision_factors])}
                </ul>
            </div>
        </div>
        """
        return html
    
    def _build_radar_chart(self):
        """Build 6-axis Dream DNA radar chart - returns plotly figure"""
        if not self.last_result:
            # Return an empty figure
            fig = go.Figure()
            fig.update_layout(title="No analysis available")
            return fig
        
        try:
            # Extract scores from agent outputs, handling FallbackAgentOutput
            scores = {}
            
            # Clarity score
            if not isinstance(self.last_result.dream_understanding, FallbackAgentOutput):
                scores['Clarity'] = self.last_result.dream_understanding.clarity_score
            else:
                scores['Clarity'] = 0.5  # Default fallback
            
            # Market score
            if not isinstance(self.last_result.market_analysis, FallbackAgentOutput):
                scores['Market'] = self.last_result.market_analysis.opportunity_score
            else:
                scores['Market'] = 0.5
            
            # Resources score
            if not isinstance(self.last_result.resource_analysis, FallbackAgentOutput):
                scores['Resources'] = self.last_result.resource_analysis.resource_feasibility
            else:
                scores['Resources'] = 0.5
            
            # Risk score (inverted)
            if not isinstance(self.last_result.risk_assessment, FallbackAgentOutput):
                scores['Risk'] = 1.0 - self.last_result.risk_assessment.risk_score
            else:
                scores['Risk'] = 0.5
            
            # Technology score (inverted from complexity)
            if not isinstance(self.last_result.technology_assessment, FallbackAgentOutput):
                scores['Technology'] = 1.0 - self.last_result.technology_assessment.build_complexity_score
            else:
                scores['Technology'] = 0.5
            
            # Innovation score
            if not isinstance(self.last_result.innovation_assessment, FallbackAgentOutput):
                scores['Innovation'] = self.last_result.innovation_assessment.novelty_score
            else:
                scores['Innovation'] = 0.5
            
            # Ensure all scores are between 0 and 1
            for key in scores:
                scores[key] = max(0, min(1, scores[key]))
            
            # Create radar chart
            fig = go.Figure(data=go.Scatterpolar(
                r=[scores[k]*100 for k in scores.keys()],
                theta=list(scores.keys()),
                fill='toself',
                name='Analysis Score',
                line=dict(color='#3b82f6', width=2),
                fillcolor='rgba(59, 130, 246, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=10)
                    ),
                    bgcolor='rgba(243, 244, 246, 0.5)'
                ),
                height=400,
                font=dict(size=11),
                title="Dream DNA Analysis - 6 Dimensions",
                showlegend=False,
                margin=dict(l=80, r=80, t=80, b=80)
            )
            
            return fig
        except Exception as e:
            # Return error figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error generating radar chart: {str(e)}",
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(title="Error")
            return fig
    
    def _build_agent_table(self) -> str:
        """Build agent voting table with confidence scores"""
        if not self.last_result:
            return "<div style='font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>No analysis available</div>"
        
        try:
            agents_data = []
            
            # Helper function to safely get agent confidence and reasoning
            def safe_get_agent_info(agent_output, agent_name):
                if isinstance(agent_output, FallbackAgentOutput):
                    return (agent_name, 0.5, agent_output.error.error_message)
                else:
                    return (agent_name, agent_output.confidence, agent_output.reasoning)
            
            agents_data = [
                safe_get_agent_info(self.last_result.dream_understanding, "Dream Understanding"),
                safe_get_agent_info(self.last_result.market_analysis, "Market Analysis"),
                safe_get_agent_info(self.last_result.resource_analysis, "Resource Analysis"),
                safe_get_agent_info(self.last_result.risk_assessment, "Risk Assessment"),
                safe_get_agent_info(self.last_result.technology_assessment, "Technology Assessment"),
                safe_get_agent_info(self.last_result.innovation_assessment, "Innovation Assessment"),
                safe_get_agent_info(self.last_result.execution_plan, "Execution Plan"),
                safe_get_agent_info(self.last_result.reality_synthesis, "Reality Synthesis"),
                safe_get_agent_info(self.last_result.final_decision, "Final Decision"),
                safe_get_agent_info(self.last_result.roadmap, "Roadmap"),
            ]
            
            html = """
            <table style="width: 100%; border-collapse: collapse; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                <thead>
                    <tr style="background-color: #f3f4f6; border-bottom: 2px solid #d1d5db;">
                        <th style="padding: 12px; text-align: left; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">Agent</th>
                        <th style="padding: 12px; text-align: center; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">Confidence</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">Key Insight</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for agent_name, confidence, reasoning in agents_data:
                conf_pct = confidence * 100
                color = "#10b981" if confidence > 0.7 else "#f59e0b" if confidence > 0.4 else "#ef4444"
                insight = reasoning[:80] if reasoning else "No insight"
                
                html += f"""
                    <tr style="border-bottom: 1px solid #e5e7eb; hover: background-color: #f9fafb;">
                        <td style="padding: 12px; font-weight: 500; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">{agent_name}</td>
                        <td style="padding: 12px; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                            <span style="background-color: {color}; color: white; padding: 4px 12px; 
                                         border-radius: 20px; font-weight: 600; font-size: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                                {conf_pct:.0f}%
                            </span>
                        </td>
                        <td style="padding: 12px; color: #374151; max-width: 300px; word-wrap: break-word; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                            {insight}...
                        </td>
                    </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
            return html
        except Exception as e:
            return f"<div style='background: #fef2f2; color: #991b1b; padding: 16px; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>Error generating agent table: {str(e)}</div>"
    
    def _build_roadmap_timeline(self) -> str:
        """Build 6-month roadmap timeline"""
        if not self.last_result:
            return "<div style='font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>No roadmap available</div>"
        
        # Extract phases from roadmap
        roadmap = self.last_result.roadmap
        if isinstance(roadmap, FallbackAgentOutput):
            return "<div style='font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>No roadmap available</div>"
        
        phases = [
            roadmap.week_1_actions,
            roadmap.month_1_goals,
            roadmap.month_3_milestones,
            roadmap.month_6_vision
        ]
        
        html = """
        <div style="padding: 20px; background: #f9fafb; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <h3 style="margin-top: 0; margin-bottom: 20px; color: #1f2937; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-weight: 600;">6-Month Roadmap</h3>
        """
        
        for i, phase in enumerate(phases[:4]):  # Show first 4 phases
            html += f"""
            <div style="display: flex; margin-bottom: 20px; align-items: flex-start; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                <div style="width: 40px; height: 40px; background: #3b82f6; color: white;
                            border-radius: 50%; display: flex; align-items: center; justify-content: center;
                            font-weight: bold; margin-right: 16px; flex-shrink: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    {i+1}
                </div>
                <div style="flex: 1; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    <h4 style="margin: 0 0 8px 0; color: #1f2937; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-weight: 600;">
                        {phase.name}
                    </h4>
                    <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-weight: 500;">
                        {phase.duration_weeks} weeks
                    </p>
                    <ul style="margin: 0; padding-left: 20px; color: #374151; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            """
            
            if hasattr(phase, 'milestones') and phase.milestones:
                for milestone in phase.milestones[:3]:
                    html += f"<li style='margin-bottom: 4px; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>{milestone}</li>"
            
            html += """
                    </ul>
                </div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def export_analysis_json(self) -> str:
        """Export analysis as JSON"""
        if not self.last_result:
            return json.dumps({"error": "No analysis available"}, indent=2)
        
        return self.last_result.model_dump_json(indent=2)
    
    def compute_adjusted_feasibility(
        self,
        budget_multiplier: float = 1.0,
        team_size: int = 5,
        timeline_months: int = 6
    ) -> Dict[str, Any]:
        """
        Compute adjusted feasibility based on what-if parameters
        
        Args:
            budget_multiplier: Budget adjustment factor (0.5 to 2.0)
            team_size: Number of team members (1 to 50)
            timeline_months: Project timeline in months (3 to 24)
        
        Returns:
            Dict with adjusted feasibility and explanations
        """
        if not self.last_result:
            return {
                "error": "No analysis available",
                "adjusted_feasibility": 0.5,
                "factors": []
            }
        
        # Start with base feasibility
        adjusted = self.base_feasibility
        factors = []
        
        # Budget adjustment: more budget increases feasibility (up to 25%)
        if budget_multiplier >= 1.0:
            budget_boost = min(0.25, (budget_multiplier - 1.0) * 0.25)
            adjusted += budget_boost
            if budget_boost > 0:
                factors.append(f"✅ Increased budget adds {budget_boost*100:.0f}% confidence")
        else:
            budget_penalty = max(-0.15, (budget_multiplier - 1.0) * 0.15)
            adjusted += budget_penalty
            if budget_penalty < 0:
                factors.append(f"⚠️ Reduced budget costs {abs(budget_penalty)*100:.0f}% feasibility")
        
        # Team size adjustment: optimal team is 5-8 people
        optimal_team_size = 6
        if team_size < 1:
            team_size = 1
        elif team_size > 50:
            team_size = 50
        
        team_score = 1.0 - (abs(team_size - optimal_team_size) / optimal_team_size) * 0.3
        team_adjustment = team_score - 1.0  # This will be negative if not optimal
        adjusted += team_adjustment
        
        if team_size < optimal_team_size:
            factors.append(f"⚠️ Small team ({team_size} people) may slow execution")
        elif team_size > optimal_team_size:
            factors.append(f"⚠️ Large team ({team_size} people) adds coordination overhead")
        else:
            factors.append(f"✅ Team size ({team_size} people) is well-balanced")
        
        # Timeline adjustment: shorter timeline increases urgency/risk
        if timeline_months < 6:
            timeline_penalty = (6 - timeline_months) * 0.03
            adjusted -= timeline_penalty
            factors.append(f"⚠️ Aggressive {timeline_months}-month timeline adds risk")
        elif timeline_months > 12:
            timeline_boost = min(0.1, (timeline_months - 12) * 0.02)
            adjusted += timeline_boost
            factors.append(f"✅ Extended {timeline_months}-month timeline provides flexibility")
        else:
            factors.append(f"✅ {timeline_months}-month timeline is realistic")
        
        # Clamp to valid range
        adjusted = max(0.0, min(1.0, adjusted))
        
        return {
            "adjusted_feasibility": adjusted,
            "base_feasibility": self.base_feasibility,
            "factors": factors,
            "team_size": team_size,
            "timeline_months": timeline_months,
            "budget_multiplier": budget_multiplier
        }


async def run_analysis(dream_text, idea_name, target_market, budget, timeline):
    """Async wrapper for analysis"""
    ui = CreativeAppUI()
    return await ui.analyze_dream(dream_text, idea_name, target_market, budget, timeline)


def build_gradio_interface():
    """Build complete Gradio interface"""
    
    ui = CreativeAppUI()
    
    with gr.Blocks(title="CreativeApp - Dream Analysis AI", theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate")) as app:
        
        # Global styles with standard fonts
        gr.HTML("""
        <style>
            * {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            }
            body, div, p, span, label, button, input, textarea, table, h1, h2, h3, h4, h5, h6 {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            }
        </style>
        """)
        
        # Header with improved styling
        gr.Markdown("""
        <div style="text-align: center; padding: 30px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <h1 style="margin: 0; color: #1f2937; font-size: 2.5em; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-weight: 700;">🚀 CreativeApp</h1>
            <p style="margin: 10px 0 0 0; color: #6b7280; font-size: 1.1em; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-weight: 500;">
                AI-Powered Dream & Idea Analysis Platform
            </p>
            <p style="margin: 8px 0 0 0; color: #9ca3af; font-size: 0.95em; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-weight: 400;">
                Transform your business ideas into actionable insights using 10 specialized AI agents
            </p>
        </div>
        """)
        
        # Input Section
        gr.Markdown("## 📝 Dream Description", elem_classes="")
        with gr.Group():
            with gr.Row():
                dream_text = gr.Textbox(
                    label="Your Dream/Idea",
                    placeholder="Describe your business idea, startup concept, or innovation...",
                    lines=4,
                    scale=2
                )
            
            with gr.Row():
                idea_name = gr.Textbox(
                    label="Project Name",
                    placeholder="e.g., AI Customer Support Platform",
                    scale=1
                )
                target_market = gr.Textbox(
                    label="Target Market",
                    placeholder="e.g., SMB B2B SaaS",
                    scale=1
                )
            
            with gr.Row():
                budget_range = gr.Dropdown(
                    label="Budget Range",
                    choices=["$10K-$50K", "$50K-$100K", "$100K-$250K", "$250K-$500K", "$500K+"],
                    value="$50K-$100K",
                    scale=1
                )
                timeline = gr.Dropdown(
                    label="Timeline",
                    choices=["3 months", "6 months", "12 months", "18 months", "24 months"],
                    value="6 months",
                    scale=1
                )
        
        # Analyze Button
        analyze_btn = gr.Button("🔮 Analyze Dream", size="lg", variant="primary")
        
        # Status/Loading with improved styling
        status = gr.Textbox(
            label="Status",
            interactive=False,
            value="✅ Ready for analysis",
            lines=2
        )
        
        # Output Tabs
        with gr.Tabs():
            
            # Tab 1: Decision & Feasibility
            with gr.TabItem("💡 Decision & Feasibility"):
                decision_output = gr.HTML(label="Decision Card")
            
            # Tab 2: Analysis Visualization
            with gr.TabItem("📊 Dream DNA Analysis"):
                radar_output = gr.Plot(label="Radar Chart")
            
            # Tab 3: Agent Details
            with gr.TabItem("🤖 Agent Analysis"):
                agent_table = gr.HTML(label="Agent Voting Table")
            
            # Tab 4: Roadmap
            with gr.TabItem("📅 Roadmap"):
                roadmap_output = gr.HTML(label="6-Month Roadmap")
            
            # Tab 5: Export
            with gr.TabItem("💾 Export"):
                with gr.Row():
                    export_json = gr.Button("📥 Export as JSON")
                json_output = gr.Code(label="JSON Export", language="json", lines=20)
        
        # What-If Simulator Section
        gr.Markdown("""
        ---
        ## 🎯 What-If Simulator
        
        Adjust parameters to see how budget, team size, and timeline impact feasibility.
        """)
        
        with gr.Group():
            with gr.Row():
                budget_slider = gr.Slider(
                    label="💰 Budget Multiplier",
                    minimum=0.5,
                    maximum=2.0,
                    value=1.0,
                    step=0.1,
                    info="0.5x = Limited Budget | 1.0x = Original Budget | 2.0x = Double Budget"
                )
            
            with gr.Row():
                team_slider = gr.Slider(
                    label="👥 Team Size",
                    minimum=1,
                    maximum=50,
                    value=5,
                    step=1,
                    info="Optimal: 5-8 people. 1-3 = Solo/Small | 5-8 = Optimal | 10+ = Large"
                )
            
            with gr.Row():
                timeline_slider = gr.Slider(
                    label="📅 Timeline (Months)",
                    minimum=3,
                    maximum=24,
                    value=6,
                    step=1,
                    info="3-5 = Aggressive | 6-12 = Realistic | 15-24 = Flexible"
                )
            
            recompute_btn = gr.Button("🔄 Recompute Feasibility", variant="secondary", size="lg")
        
        # What-If Results
        whatif_results = gr.HTML(label="What-If Analysis")
        
        # Analysis History
        with gr.Accordion(label="📋 Analysis History", open=False):
            history_output = gr.Textbox(
                label="Recent Analyses",
                interactive=False,
                lines=6,
                value="No analyses yet"
            )
        
        # Footer
        gr.Markdown("""
        ---
        <div style="text-align: center; padding: 30px 0; border-top: 1px solid #e5e7eb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <div style="margin-bottom: 12px; font-size: 0.95em; color: #1f2937; font-weight: 500; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                <span style="color: #3b82f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">CreativeApp v1.0</span> — AI-Powered Dream Analysis System
            </div>
            <div style="font-size: 0.85em; color: #6b7280; line-height: 1.6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                🤖 Powered by 10 specialized AI agents + semantic knowledge retrieval  
                <br/>📊 Real-time feasibility analysis with what-if simulations
                <br/>💡 <em>Transform your ideas into actionable insights</em>
            </div>
            <div style="margin-top: 16px; font-size: 0.8em; color: #9ca3af; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            </div>
        </div>
        """)
        
        # Event Handlers
        def analyze_and_update(dream, idea, market, budget, timeline_val):
            """Handle analysis button click"""
            try:
                # Update status
                import asyncio
                
                # Use asyncio to run the async function
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Show loading state
                status_msg = "⏳ Analyzing dream with 10 AI agents..."
                
                decision, radar, agents, roadmap, final_status = loop.run_until_complete(
                    ui.analyze_dream(dream, idea, market, budget, timeline_val)
                )
                
                # Update history
                history_text = "Recent Analyses:\n"
                for h in ui.analysis_history[-5:]:
                    history_text += f"• {h['idea_name']} - {h['decision']}\n"
                
                return decision, radar, agents, roadmap, final_status, history_text
            except Exception as e:
                error_html = f"<div style='background: #fef2f2; color: #991b1b; padding: 16px; border-radius: 8px; border-left: 4px solid #dc2626; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'><strong>❌ Error:</strong> {str(e)}</div>"
                return error_html, go.Figure(), error_html, "", f"Error: {str(e)}", "Error occurred"
        
        def export_json_handler():
            """Export current analysis as JSON"""
            return ui.export_analysis_json()
        
        def recompute_whatif(budget, team, timeline):
            """Recompute feasibility based on what-if parameters"""
            result = ui.compute_adjusted_feasibility(budget, team, timeline)
            
            if "error" in result:
                return f"<div style='background: #fef2f2; color: #991b1b; padding: 16px; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>{result['error']}</div>"
            
            # Build HTML for what-if results
            base_pct = result['base_feasibility'] * 100
            adjusted_pct = result['adjusted_feasibility'] * 100
            change = adjusted_pct - base_pct
            change_indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            color = "#10b981" if adjusted_pct > 70 else "#f59e0b" if adjusted_pct > 40 else "#ef4444"
            
            factors_html = "\n".join([f"<li style='margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif;'>{factor}</li>" for factor in result['factors']])
            
            html = f"""
            <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
                        border: 2px solid {color};
                        border-radius: 12px;
                        padding: 24px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: white; padding: 16px; border-radius: 8px; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                        <div style="color: #6b7280; font-size: 12px; font-weight: 600; margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">BASE FEASIBILITY</div>
                        <div style="color: #1f2937; font-size: 28px; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">{base_pct:.0f}%</div>
                    </div>
                    <div style="background: white; padding: 16px; border-radius: 8px; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                        <div style="color: #6b7280; font-size: 12px; font-weight: 600; margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">ADJUSTED FEASIBILITY</div>
                        <div style="color: {color}; font-size: 28px; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">{adjusted_pct:.0f}%</div>
                    </div>
                    <div style="background: white; padding: 16px; border-radius: 8px; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                        <div style="color: #6b7280; font-size: 12px; font-weight: 600; margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">CHANGE</div>
                        <div style="color: {color}; font-size: 28px; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">{change_indicator} {change:+.0f}%</div>
                    </div>
                </div>
                
                <div style="background: white; border-radius: 8px; padding: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    <h4 style="margin: 0 0 12px 0; color: #1f2937; font-size: 14px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">📊 Impact Analysis</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #374151; font-size: 13px; line-height: 1.8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                        {factors_html}
                    </ul>
                </div>
                
                <div style="background: #f0f9ff; border-left: 4px solid {color}; padding: 12px; border-radius: 4px; margin-top: 16px; font-size: 13px; color: #374151; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
                    <strong>Scenario:</strong> Team of {result['team_size']} | Budget x{result['budget_multiplier']:.1f} | {result['timeline_months']}-month timeline
                </div>
            </div>
            """
            return html
        
        # Button click handlers
        analyze_btn.click(
            fn=analyze_and_update,
            inputs=[dream_text, idea_name, target_market, budget_range, timeline],
            outputs=[decision_output, radar_output, agent_table, roadmap_output, status, history_output]
        )
        
        export_json.click(
            fn=export_json_handler,
            outputs=json_output
        )
        
        recompute_btn.click(
            fn=recompute_whatif,
            inputs=[budget_slider, team_slider, timeline_slider],
            outputs=whatif_results
        )
    
    return app


def main():
    """Main entry point"""
    print("🚀 Starting CreativeApp UI...")
    print("📍 Open http://localhost:7860 in your browser")
    
    app = build_gradio_interface()
    app.queue()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate"
        )
    )


if __name__ == "__main__":
    main()
