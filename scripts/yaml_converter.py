"""
YAML Converter
Converts between Testmo API format and Git YAML format
"""
from datetime import datetime
from html.parser import HTMLParser
from typing import Dict, List, Any, Optional
from pathlib import Path
import re


class HTMLStripper(HTMLParser):
    """HTML parser that extracts plain text from HTML"""

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return ''.join(self.text)


def strip_html(html_string: str) -> str:
    """Remove HTML tags and return clean text"""
    if not html_string:
        return ""
    if not isinstance(html_string, str):
        return str(html_string)

    try:
        s = HTMLStripper()
        s.feed(html_string)
        # Clean up whitespace
        text = s.get_data().strip()
        # Normalize multiple spaces/newlines
        text = re.sub(r'\s+', ' ', text)
        return text
    except Exception:
        # Fallback: simple regex strip
        return re.sub(r'<[^>]+>', '', html_string).strip()


def parse_html_list_items(html_string: str) -> List[str]:
    """Parse HTML <li> items into a Python list"""
    if not html_string:
        return []
    if not isinstance(html_string, str):
        return []

    # Find all <li> content (handles both <li>...</li> and <li>...<li>)
    items = re.findall(r'<li[^>]*>(.*?)</li>', html_string, re.DOTALL | re.IGNORECASE)

    # If no <li> tags found, try <p> tags
    if not items:
        items = re.findall(r'<p[^>]*>(.*?)</p>', html_string, re.DOTALL | re.IGNORECASE)

    # If still nothing, try splitting by <br> or newlines
    if not items:
        # Remove tags and split by newlines
        text = strip_html(html_string)
        items = [line.strip() for line in text.split('\n') if line.strip()]
        return items

    # Strip HTML from each item and clean up
    result = []
    for item in items:
        cleaned = strip_html(item).strip()
        # Remove leading bullets, dashes, numbers
        cleaned = re.sub(r'^[\d\.\)\-\*\•]+\s*', '', cleaned).strip()
        if cleaned:
            result.append(cleaned)

    return result


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
    def testmo_to_yaml(testmo_case: Dict[str, Any], feature: str = "general", existing_file: Optional[Path] = None) -> Dict[str, Any]:
        """Convert Testmo format to YAML format.

        Args:
            testmo_case: Case data from Testmo API
            feature: Feature name
            existing_file: If provided, extract test_id from filename (e.g., TC001 from TC001-name.yml)

        Testmo API returns these custom fields at the TOP LEVEL:
        - custom_description: HTML string with description
        - custom_preconditions: HTML string with <li> items
        - custom_steps: Array of objects with text1 (actions), text3 (expected), display_order
        - custom_priority: Integer (1=critical, 2=high, 3=medium, 4=low)
        - custom_notes: Optional HTML string
        """
        # Generate test ID
        testmo_id = testmo_case.get("id", 0)

        # If updating existing file, preserve the original test ID
        if existing_file:
            # Extract TC001 from "TC001-max-charge-limit-banner.yml"
            match = re.match(r'^(TC\d+)', existing_file.stem)
            test_id = match.group(1) if match else f"TC{testmo_id:05d}"
        else:
            # New file - use Testmo ID
            test_id = f"TC{testmo_id:05d}"

        # Priority mapping
        priority_map = {1: "critical", 2: "high", 3: "medium", 4: "low"}
        priority = priority_map.get(testmo_case.get("custom_priority", 3), "medium")

        # Extract platforms and regions (default values)
        platforms = ["iOS", "Android"]
        regions = ["USA"]

        # Parse description
        description = strip_html(testmo_case.get("custom_description", ""))

        # Parse preconditions
        precon_html = testmo_case.get("custom_preconditions", "")
        preconditions = []
        for item in parse_html_list_items(precon_html):
            preconditions.append({"description": item})

        # Parse steps
        steps = []
        custom_steps = testmo_case.get("custom_steps", [])
        if custom_steps and isinstance(custom_steps, list):
            for step_obj in custom_steps:
                if not isinstance(step_obj, dict):
                    continue

                actions_html = step_obj.get("text1", "")
                expected_html = step_obj.get("text3", "")

                action_items = parse_html_list_items(actions_html)
                expected_items = parse_html_list_items(expected_html)

                # Create step if we have actions
                if action_items:
                    step = {
                        "id": step_obj.get("display_order", len(steps) + 1),
                        "action": " -> ".join(action_items),
                        "expected": " | ".join(expected_items) if expected_items else "See expected results"
                    }
                    steps.append(step)

        # Build YAML structure
        yaml_case = {
            "metadata": {
                "id": test_id,
                "name": testmo_case.get("name", "Untitled"),
                "feature": feature,
                "priority": priority,
                "platforms": platforms,
                "regions": regions,
                "tags": [],
                "created": YAMLConverter._format_date(testmo_case.get("created_at")),
                "updated": YAMLConverter._format_date(testmo_case.get("updated_at")),
                "author": f"user_{testmo_case.get('created_by', 'unknown')}",
                "testmo_id": testmo_id
            }
        }

        # Add optional fields only if they have content
        if description:
            yaml_case["description"] = description

        if preconditions:
            yaml_case["preconditions"] = preconditions

        if steps:
            yaml_case["steps"] = steps

        return yaml_case
    
    @staticmethod
    def yaml_to_testmo(yaml_case: Dict[str, Any]) -> Dict[str, Any]:
        """Convert YAML format to Testmo format.

        Builds HTML custom fields for Testmo API:
        - custom_description: <p> tags
        - custom_preconditions: <ul><li> tags
        - custom_steps[].text1: <ol><li> tags (numbered actions)
        - custom_steps[].text3: <ul><li> tags (expected results)
        - custom_priority: Integer (1=critical, 2=high, 3=medium, 4=low)
        """
        metadata = yaml_case.get("metadata", {})

        # Priority mapping (reverse)
        priority_map = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        priority = priority_map.get(metadata.get("priority", "medium"), 3)

        # Build description HTML
        description = yaml_case.get("description", "")
        if description:
            custom_description = f"<p>{description}</p>"
        else:
            custom_description = ""

        # Build preconditions HTML
        preconditions = yaml_case.get("preconditions", [])
        if preconditions:
            precon_items = []
            for precon in preconditions:
                desc = precon.get("description", "")
                if desc:
                    precon_items.append(f"<li>{desc}</li>")
            custom_preconditions = "<ul>" + "".join(precon_items) + "</ul>" if precon_items else ""
        else:
            custom_preconditions = ""

        # Build steps HTML
        steps = yaml_case.get("steps", [])
        custom_steps = []

        if steps:
            for step in steps:
                step_id = step.get("id", 1)
                action = step.get("action", "")
                expected = step.get("expected", "")

                # Build text1 (actions) - split by -> if combined
                actions = [a.strip() for a in action.split("->")] if "->" in action else [action]
                text1_items = [f"<li>{a}</li>" for a in actions if a]
                text1 = "<ol>" + "".join(text1_items) + "</ol>" if text1_items else ""

                # Build text3 (expected) - split by | if combined
                expected_list = [e.strip() for e in expected.split("|")] if "|" in expected else [expected]
                text3_items = [f"<li>{e}</li>" for e in expected_list if e]
                text3 = "<ul>" + "".join(text3_items) + "</ul>" if text3_items else ""

                custom_steps.append({
                    "text1": text1,
                    "text2": None,
                    "text3": text3,
                    "text4": None,
                    "display_order": step_id
                })

        # Build Testmo case structure
        testmo_case = {
            "name": metadata.get("name", "Untitled"),
            "custom_priority": priority,
            "custom_description": custom_description,
            "custom_preconditions": custom_preconditions,
            "custom_steps": custom_steps
        }

        # Add testmo_id if it exists (for updates)
        testmo_id = metadata.get("testmo_id")
        if testmo_id:
            testmo_case["id"] = testmo_id

        return testmo_case
    
    @staticmethod
    def _generate_test_id(testmo_case: Dict[str, Any]) -> str:
        """Generate a test case ID"""
        case_id = testmo_case.get("id", 0)
        return f"TC{case_id:05d}"
    
    @staticmethod
    def _format_date(date_str: Optional[str]) -> str:
        """Format date string to YYYY-MM-DD.

        Handles: None, ISO format with Z, ISO format with timezone, datetime objects.
        """
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        try:
            if isinstance(date_str, str):
                # Remove timezone and microseconds
                dt = datetime.fromisoformat(
                    date_str.replace("Z", "+00:00").split("+")[0].split(".")[0]
                )
                return dt.strftime("%Y-%m-%d")
            elif isinstance(date_str, datetime):
                return date_str.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            pass

        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _extract_author(testmo_case: Dict[str, Any]) -> str:
        """Extract author - handles both object and ID formats from API"""
        created_by = testmo_case.get("created_by")

        if created_by is None:
            return "unknown"

        # Handle object format: {"id": 1, "email": "user@example.com", "name": "User Name"}
        if isinstance(created_by, dict):
            email = created_by.get("email", "")
            if email:
                return email.split("@")[0]
            name = created_by.get("name", "")
            if name:
                return name.lower().replace(" ", ".")
            return f"user_{created_by.get('id', 'unknown')}"

        # Handle integer ID format
        if isinstance(created_by, int):
            return f"user_{created_by}"

        # Handle string format (could be email or username)
        if isinstance(created_by, str):
            if "@" in created_by:
                return created_by.split("@")[0]
            return created_by

        return "unknown"

    @staticmethod
    def _extract_priority(testmo_case: Dict[str, Any], custom_fields: Dict[str, Any]) -> str:
        """Extract priority from custom_priority or priority_id"""
        # Check custom_priority first (integer: 1=Critical, 2=High, 3=Medium, 4=Low)
        custom_priority = custom_fields.get("custom_priority")
        if custom_priority is not None:
            if isinstance(custom_priority, int):
                return YAMLConverter.PRIORITY_FROM_TESTMO.get(custom_priority, "medium")
            if isinstance(custom_priority, str):
                # Handle string values like "critical", "high", etc.
                return custom_priority.lower() if custom_priority.lower() in YAMLConverter.PRIORITY_TO_TESTMO else "medium"

        # Fall back to priority_id
        priority_id = testmo_case.get("priority_id", 3)
        return YAMLConverter.PRIORITY_FROM_TESTMO.get(priority_id, "medium")

    @staticmethod
    def _extract_description(testmo_case: Dict[str, Any], custom_fields: Dict[str, Any]) -> str:
        """Extract description from custom_description or description field"""
        # Try custom_description first (may contain HTML)
        custom_desc = custom_fields.get("custom_description")
        if custom_desc and isinstance(custom_desc, str):
            return strip_html(custom_desc)

        # Fall back to regular description
        description = testmo_case.get("description", "")
        if description and isinstance(description, str):
            return strip_html(description)

        return ""

    @staticmethod
    def _extract_notes(custom_fields: Dict[str, Any]) -> str:
        """Extract notes from custom_notes field"""
        custom_notes = custom_fields.get("custom_notes")
        if custom_notes and isinstance(custom_notes, str):
            return strip_html(custom_notes)
        return ""

    @staticmethod
    def _parse_custom_steps(custom_fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse steps from custom_steps array with HTML content"""
        custom_steps = custom_fields.get("custom_steps")
        if not custom_steps:
            return []

        if not isinstance(custom_steps, list):
            return []

        steps = []
        for idx, step_data in enumerate(custom_steps):
            if not isinstance(step_data, dict):
                continue

            # Get display order or use index
            step_id = step_data.get("display_order")
            if step_id is None:
                step_id = idx + 1
            elif not isinstance(step_id, int):
                try:
                    step_id = int(step_id)
                except (ValueError, TypeError):
                    step_id = idx + 1

            # Parse text1 (actions) - may contain <ol>/<li> HTML
            actions_html = step_data.get("text1", "")
            action_items = parse_html_list_items(actions_html)
            action = " ".join(action_items) if action_items else strip_html(actions_html)

            # Parse text3 (expected results) - may contain <ul>/<li> HTML
            expected_html = step_data.get("text3", "")
            expected_items = parse_html_list_items(expected_html)
            expected = " ".join(expected_items) if expected_items else strip_html(expected_html)

            # Only add step if it has content
            if action or expected:
                step = {
                    "id": step_id,
                    "action": action or "Perform action",
                    "expected": expected or "Verify expected result"
                }
                steps.append(step)

        # Sort steps by ID
        steps.sort(key=lambda x: x["id"])

        # Renumber steps to be sequential starting from 1
        for idx, step in enumerate(steps):
            step["id"] = idx + 1

        return steps

    @staticmethod
    def _parse_custom_preconditions(custom_fields: Dict[str, Any]) -> List[Dict[str, str]]:
        """Parse preconditions from custom_preconditions HTML field"""
        custom_preconditions = custom_fields.get("custom_preconditions")
        if not custom_preconditions:
            return []

        if not isinstance(custom_preconditions, str):
            return []

        # Parse HTML list items
        items = parse_html_list_items(custom_preconditions)

        # If no list items found, try to split by sentences or use as single item
        if not items:
            text = strip_html(custom_preconditions)
            if text:
                # Split by common separators
                items = [s.strip() for s in re.split(r'[;\n]', text) if s.strip()]
                if not items:
                    items = [text]

        return [{"description": item} for item in items if item]

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

        # Ensure tags is a list
        if not isinstance(tags, list):
            tags = []

        for tag in tags:
            if not isinstance(tag, str):
                continue
            tag_lower = tag.lower()
            if "ios" in tag_lower:
                platforms.append("iOS")
            if "android" in tag_lower:
                platforms.append("Android")

        # Check custom fields as fallback
        custom_fields = testmo_case.get("custom_fields")
        if isinstance(custom_fields, dict):
            platform_field = custom_fields.get("platform", "")
            if isinstance(platform_field, str):
                if "ios" in platform_field.lower():
                    platforms.append("iOS")
                if "android" in platform_field.lower():
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

        # Ensure tags is a list
        if not isinstance(tags, list):
            tags = []

        region_map = {
            "usa": "USA",
            "canada": "Canada",
            "mexico": "Mexico",
            "brazil": "Brazil"
        }

        for tag in tags:
            if not isinstance(tag, str):
                continue
            tag_lower = tag.lower()
            for key, value in region_map.items():
                if key in tag_lower:
                    regions.append(value)

        # Check custom fields as fallback
        custom_fields = testmo_case.get("custom_fields")
        if isinstance(custom_fields, dict):
            region_field = custom_fields.get("region", "")
            if isinstance(region_field, str):
                for key, value in region_map.items():
                    if key in region_field.lower():
                        regions.append(value)

        # Default to USA if none specified
        if not regions:
            regions = ["USA"]

        return list(set(regions))
    
    @staticmethod
    def _extract_automation_info(testmo_case: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract automation information"""
        custom_fields = testmo_case.get("custom_fields")

        # Ensure custom_fields is a dict
        if not isinstance(custom_fields, dict):
            return None

        framework = custom_fields.get("automation_framework")
        coverage = custom_fields.get("automation_coverage", "none")

        # Ensure values are strings
        if framework and not isinstance(framework, str):
            framework = str(framework)
        if coverage and not isinstance(coverage, str):
            coverage = str(coverage)

        if framework or (coverage and coverage != "none"):
            return {
                "framework": framework or "unknown",
                "coverage": coverage or "none"
            }

        return None
    
    @staticmethod
    def _extract_traceability(testmo_case: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract traceability links"""
        custom_fields = testmo_case.get("custom_fields")

        # Ensure custom_fields is a dict
        if not isinstance(custom_fields, dict):
            return None

        traceability = {}

        clickup_task = custom_fields.get("clickup_task")
        if clickup_task and isinstance(clickup_task, str):
            traceability["clickup_task"] = clickup_task

        user_story = custom_fields.get("user_story")
        if user_story and isinstance(user_story, str):
            traceability["user_story"] = user_story

        jira_ticket = custom_fields.get("jira_ticket")
        if jira_ticket and isinstance(jira_ticket, str):
            traceability["jira_ticket"] = jira_ticket

        figma_link = custom_fields.get("figma_link")
        if figma_link and isinstance(figma_link, str):
            traceability["figma_link"] = figma_link

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
