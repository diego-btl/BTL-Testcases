"""
YAML Converter
Converts between Testmo API format and Git YAML format
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class YAMLConverter:
    """Converts between Testmo and YAML formats"""
    
    # Priority mappings
    PRIORITY_TO_TESTMO = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4
    }
    
    PRIORITY_FROM_TESTMO = {v: k for k, v in PRIORITY_TO_TESTMO.items()}
    
    # State mappings
    STATE_TO_TESTMO = {
        "draft": 1,
        "review": 2,
        "approved": 3,
        "active": 4,
        "deprecated": 5
    }
    
    STATE_FROM_TESTMO = {v: k for k, v in STATE_TO_TESTMO.items()}
    
    @staticmethod
    def testmo_to_yaml(testmo_case: Dict[str, Any], feature: str = "general") -> Dict[str, Any]:
        """Convert Testmo case to YAML format"""
        
        # Parse steps from description/precondition fields
        steps = YAMLConverter._parse_steps_from_testmo(testmo_case)
        preconditions = YAMLConverter._parse_preconditions_from_testmo(testmo_case)
        
        # Extract platforms from custom fields or tags
        platforms = YAMLConverter._extract_platforms(testmo_case)
        
        # Extract regions from tags or custom fields
        regions = YAMLConverter._extract_regions(testmo_case)
        
        yaml_case = {
            "metadata": {
                "id": YAMLConverter._generate_test_id(testmo_case),
                "name": testmo_case.get("name", "Untitled Test"),
                "feature": feature,
                "priority": YAMLConverter.PRIORITY_FROM_TESTMO.get(
                    testmo_case.get("priority_id", 3), "medium"
                ),
                "platforms": platforms,
                "regions": regions,
                "tags": testmo_case.get("tags", []),
                "created": YAMLConverter._format_date(testmo_case.get("created_at")),
                "updated": YAMLConverter._format_date(testmo_case.get("updated_at")),
                "author": testmo_case.get("created_by", {}).get("email", "unknown").split("@")[0],
                "testmo_id": testmo_case.get("id")
            }
        }
        
        if preconditions:
            yaml_case["preconditions"] = preconditions
        
        if steps:
            yaml_case["steps"] = steps
        
        # Add automation info if available
        automation_info = YAMLConverter._extract_automation_info(testmo_case)
        if automation_info:
            yaml_case["automation"] = automation_info
        
        # Add traceability
        traceability = YAMLConverter._extract_traceability(testmo_case)
        if traceability:
            yaml_case["traceability"] = traceability
        
        return yaml_case
    
    @staticmethod
    def yaml_to_testmo(yaml_case: Dict[str, Any]) -> Dict[str, Any]:
        """Convert YAML format to Testmo case format"""
        
        metadata = yaml_case.get("metadata", {})
        steps = yaml_case.get("steps", [])
        preconditions = yaml_case.get("preconditions", [])
        
        # Build description from steps
        description = YAMLConverter._build_testmo_description(steps, preconditions)
        
        testmo_case = {
            "name": metadata.get("name", "Untitled Test"),
            "priority_id": YAMLConverter.PRIORITY_TO_TESTMO.get(
                metadata.get("priority", "medium"), 3
            ),
            "state_id": YAMLConverter.STATE_TO_TESTMO.get("active", 4),
            "description": description,
        }
        
        # Add tags
        tags = metadata.get("tags", [])
        platforms = metadata.get("platforms", [])
        regions = metadata.get("regions", [])
        
        # Combine all into tags
        all_tags = tags + [f"platform:{p.lower()}" for p in platforms] + [f"region:{r.lower()}" for r in regions]
        if all_tags:
            testmo_case["tags"] = all_tags
        
        # Add custom fields
        custom_fields = {}
        
        # Feature as custom field
        if metadata.get("feature"):
            custom_fields["feature"] = metadata["feature"]
        
        # Add automation info
        automation = yaml_case.get("automation", {})
        if automation:
            custom_fields["automation_framework"] = automation.get("framework", "")
            custom_fields["automation_coverage"] = automation.get("coverage", "none")
        
        # Add traceability
        traceability = yaml_case.get("traceability", {})
        if traceability:
            if traceability.get("clickup_task"):
                custom_fields["clickup_task"] = traceability["clickup_task"]
            if traceability.get("user_story"):
                custom_fields["user_story"] = traceability["user_story"]
        
        if custom_fields:
            testmo_case["custom_fields"] = custom_fields
        
        return testmo_case
    
    @staticmethod
    def _generate_test_id(testmo_case: Dict[str, Any]) -> str:
        """Generate a test case ID"""
        case_id = testmo_case.get("id", 0)
        return f"TC{case_id:05d}"
    
    @staticmethod
    def _format_date(date_str: Optional[str]) -> str:
        """Format date string"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")
        
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def _parse_steps_from_testmo(testmo_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse steps from Testmo description"""
        description = testmo_case.get("description", "")
        steps = []
        
        # Try to parse numbered steps
        step_pattern = r'(\d+)\.\s*(.+?)(?=\n\d+\.|\n*$)'
        matches = re.findall(step_pattern, description, re.DOTALL)
        
        for step_num, step_text in matches:
            # Split action and expected if possible
            parts = step_text.split("Expected:", 1)
            action = parts[0].strip()
            expected = parts[1].strip() if len(parts) > 1 else "Verify step completes successfully"
            
            steps.append({
                "id": int(step_num),
                "action": action,
                "expected": expected
            })
        
        # If no steps found, create a default step
        if not steps and description:
            steps.append({
                "id": 1,
                "action": description[:200],
                "expected": "Verify expected behavior"
            })
        
        return steps
    
    @staticmethod
    def _parse_preconditions_from_testmo(testmo_case: Dict[str, Any]) -> List[Dict[str, str]]:
        """Parse preconditions from Testmo"""
        precondition = testmo_case.get("precondition", "")
        if not precondition:
            return []
        
        # Split by newlines or bullet points
        lines = [line.strip() for line in precondition.split("\n") if line.strip()]
        
        return [{"description": line.lstrip("•-*").strip()} for line in lines]
    
    @staticmethod
    def _extract_platforms(testmo_case: Dict[str, Any]) -> List[str]:
        """Extract platforms from tags or custom fields"""
        platforms = []
        tags = testmo_case.get("tags", [])
        
        for tag in tags:
            if "ios" in tag.lower():
                platforms.append("iOS")
            if "android" in tag.lower():
                platforms.append("Android")
        
        # Default to both if none specified
        if not platforms:
            platforms = ["iOS", "Android"]
        
        return list(set(platforms))
    
    @staticmethod
    def _extract_regions(testmo_case: Dict[str, Any]) -> List[str]:
        """Extract regions from tags"""
        regions = []
        tags = testmo_case.get("tags", [])
        
        region_map = {
            "usa": "USA",
            "canada": "Canada",
            "mexico": "Mexico",
            "brazil": "Brazil"
        }
        
        for tag in tags:
            tag_lower = tag.lower()
            for key, value in region_map.items():
                if key in tag_lower:
                    regions.append(value)
        
        # Default to USA if none specified
        if not regions:
            regions = ["USA"]
        
        return list(set(regions))
    
    @staticmethod
    def _extract_automation_info(testmo_case: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract automation information"""
        custom_fields = testmo_case.get("custom_fields", {})
        
        framework = custom_fields.get("automation_framework")
        coverage = custom_fields.get("automation_coverage", "none")
        
        if framework or coverage != "none":
            return {
                "framework": framework or "unknown",
                "coverage": coverage
            }
        
        return None
    
    @staticmethod
    def _extract_traceability(testmo_case: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract traceability links"""
        custom_fields = testmo_case.get("custom_fields", {})
        traceability = {}
        
        if custom_fields.get("clickup_task"):
            traceability["clickup_task"] = custom_fields["clickup_task"]
        
        if custom_fields.get("user_story"):
            traceability["user_story"] = custom_fields["user_story"]
        
        return traceability if traceability else None
    
    @staticmethod
    def _build_testmo_description(steps: List[Dict[str, Any]], preconditions: List[Dict[str, str]]) -> str:
        """Build Testmo description from steps and preconditions"""
        parts = []
        
        if preconditions:
            parts.append("**Preconditions:**")
            for pre in preconditions:
                parts.append(f"- {pre['description']}")
            parts.append("")
        
        if steps:
            parts.append("**Steps:**")
            for step in steps:
                step_id = step.get("id", 1)
                action = step.get("action", "")
                expected = step.get("expected", "")
                
                parts.append(f"{step_id}. {action}")
                if expected:
                    parts.append(f"   Expected: {expected}")
            parts.append("")
        
        return "\n".join(parts)
