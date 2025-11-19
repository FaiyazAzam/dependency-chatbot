import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# ============================================================================
# MOCK DATA STRUCTURES
# ============================================================================

# Release metadata: package -> version -> metadata
RELEASE_METADATA = {
    "auth-lib": {
        "2.1.0": {
            "notes": "Security patches for token validation. Performance improvements in JWT parsing.",
            "bump_type": "minor",
            "release_date": "2024-01-15"
        },
        "2.2.0": {
            "notes": "Added OAuth2 refresh token support. Fixed memory leak in session management.",
            "bump_type": "minor",
            "release_date": "2024-02-20"
        },
        "3.0.0": {
            "notes": "BREAKING: Removed deprecated API endpoints. New authentication flow required. Migration guide available.",
            "bump_type": "major",
            "release_date": "2024-03-10"
        }
    },
    "payments-core": {
        "3.1.0": {
            "notes": "Bug fixes for currency conversion edge cases. Improved error handling.",
            "bump_type": "minor",
            "release_date": "2024-01-22"
        },
        "3.2.0": {
            "notes": "Added support for new payment methods. Enhanced transaction logging.",
            "bump_type": "minor",
            "release_date": "2024-02-05"
        },
        "4.0.0": {
            "notes": "BREAKING: New payment gateway integration. API signature changes. Requires database migration.",
            "bump_type": "major",
            "release_date": "2024-03-18"
        }
    },
    "logging-lib": {
        "1.5.0": {
            "notes": "Fixed log rotation issue. Added structured logging support.",
            "bump_type": "minor",
            "release_date": "2024-01-10"
        },
        "1.5.1": {
            "notes": "Critical bug fix for log file corruption under high load.",
            "bump_type": "patch",
            "release_date": "2024-01-25"
        },
        "2.0.0": {
            "notes": "BREAKING: Changed default log format. New configuration schema required.",
            "bump_type": "major",
            "release_date": "2024-02-28"
        }
    }
}

# Known issues / CVE-like table: package -> version -> issues
KNOWN_ISSUES = {
    "auth-lib": {
        "2.0.0": ["CVE-2024-001: Token validation bypass vulnerability"],
        "2.0.5": ["CVE-2024-001: Token validation bypass vulnerability"],
        "2.1.0": []  # Fixed
    },
    "payments-core": {
        "3.0.0": ["CVE-2024-002: Potential race condition in transaction processing"],
        "3.1.0": []  # Fixed
    },
    "logging-lib": {
        "1.4.0": ["CVE-2024-003: Log injection vulnerability"],
        "1.5.0": []  # Fixed
    }
}

# Internal incidents: package -> version -> incidents
INTERNAL_INCIDENTS = {
    "payments-core": {
        "3.2.0": ["Incident #142: Memory leak detected in production. Root cause: improper resource cleanup in transaction handler."]
    },
    "auth-lib": {
        "2.0.0": ["Incident #89: Authentication failures during peak load. Resolved in 2.1.0."]
    },
    "logging-lib": {
        "1.4.5": ["Incident #156: Log file corruption causing service restarts. Fixed in 1.5.1."]
    }
}

# Compatibility matrix: service -> package -> version
COMPATIBILITY_MATRIX = {
    "Checkout Service": {
        "payments-core": "3.2.0",
        "auth-lib": "2.2.0",
        "logging-lib": "1.5.1"
    },
    "User Service": {
        "auth-lib": "3.0.0",
        "logging-lib": "2.0.0"
    },
    "API Gateway": {
        "auth-lib": "2.2.0",
        "logging-lib": "1.5.1"
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_version(version: str) -> tuple:
    """Parse version string into (major, minor, patch) tuple."""
    try:
        parts = version.split('.')
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except:
        return (0, 0, 0)

def get_bump_type(old_version: str, new_version: str) -> str:
    """Determine if upgrade is major, minor, or patch."""
    old = parse_version(old_version)
    new = parse_version(new_version)
    
    if new[0] > old[0]:
        return "major"
    elif new[1] > old[1]:
        return "minor"
    elif new[2] > old[2]:
        return "patch"
    else:
        return "unknown"

def check_security_issues(package: str, old_version: str, new_version: str) -> tuple:
    """Check if old version has security issues and if new version fixes them."""
    old_issues = KNOWN_ISSUES.get(package, {}).get(old_version, [])
    new_issues = KNOWN_ISSUES.get(package, {}).get(new_version, [])
    
    return old_issues, new_issues

def check_internal_incidents(package: str, old_version: str, new_version: str) -> tuple:
    """Check internal incidents for old and new versions."""
    old_incidents = INTERNAL_INCIDENTS.get(package, {}).get(old_version, [])
    new_incidents = INTERNAL_INCIDENTS.get(package, {}).get(new_version, [])
    
    return old_incidents, new_incidents

def check_compatibility(package: str, new_version: str, context: Optional[str]) -> Dict[str, Any]:
    """Check compatibility with other services."""
    compatible_services = []
    incompatible_services = []
    
    # If context mentions a service, check that service specifically
    if context:
        context_lower = context.lower()
        for service_name, packages in COMPATIBILITY_MATRIX.items():
            if service_name.lower() in context_lower:
                if package in packages:
                    service_version = packages[package]
                    compatible_services.append(f"{service_name} uses {service_version}")
                break
    
    # Check all services
    for service_name, packages in COMPATIBILITY_MATRIX.items():
        if package in packages:
            service_version = packages[package]
            new_ver = parse_version(new_version)
            service_ver = parse_version(service_version)
            
            # Same major version is generally compatible
            if new_ver[0] == service_ver[0]:
                compatible_services.append(f"{service_name} uses {service_version}")
            elif new_ver[0] > service_ver[0]:
                incompatible_services.append(f"{service_name} uses {service_version} (major version mismatch)")
    
    return {
        "compatible": compatible_services,
        "incompatible": incompatible_services
    }

# ============================================================================
# MAIN REASONING FUNCTION
# ============================================================================

def explain_version_choice(
    package: str,
    old_version: str,
    new_version: str,
    ecosystem: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a structured explanation for a version upgrade choice.
    
    Returns a dict with:
    - summary: Brief overview
    - risk_reasoning: Risk assessment
    - security_reasoning: Security considerations
    - compatibility_reasoning: Compatibility with other services
    - sources: List of source strings
    """
    
    # Determine bump type
    bump_type = get_bump_type(old_version, new_version)
    
    # Get release metadata
    release_notes = RELEASE_METADATA.get(package, {}).get(new_version, {}).get("notes", "No release notes available.")
    metadata_bump = RELEASE_METADATA.get(package, {}).get(new_version, {}).get("bump_type", bump_type)
    
    # Check security issues
    old_security_issues, new_security_issues = check_security_issues(package, old_version, new_version)
    
    # Check internal incidents
    old_incidents, new_incidents = check_internal_incidents(package, old_version, new_version)
    
    # Check compatibility
    compat_info = check_compatibility(package, new_version, context)
    
    # Build sources list
    sources = []
    if release_notes != "No release notes available.":
        sources.append(f"Release notes for {package} {new_version}")
    if old_security_issues:
        sources.append(f"Security advisories for {package} {old_version}")
    if old_incidents:
        sources.append(f"Internal incident reports for {package} {old_version}")
    if compat_info["compatible"] or compat_info["incompatible"]:
        sources.append("Internal compatibility matrix")
    
    # Build summary
    if bump_type == "major":
        summary = f"Major version upgrade from {old_version} to {new_version}. This may include breaking changes."
    elif bump_type == "minor":
        summary = f"Minor version upgrade from {old_version} to {new_version}. New features and improvements expected."
    else:
        summary = f"Patch upgrade from {old_version} to {new_version}. Bug fixes and security patches."
    
    # Risk reasoning
    risk_reasoning = []
    if bump_type == "major":
        risk_reasoning.append(f"This is a major version upgrade, which typically includes breaking changes. Review the release notes carefully and plan for migration.")
    elif bump_type == "minor":
        risk_reasoning.append(f"This is a minor version upgrade, which should be backward compatible but may introduce new features.")
    else:
        risk_reasoning.append(f"This is a patch upgrade, which should be low risk and focused on bug fixes.")
    
    if old_incidents:
        risk_reasoning.append(f"⚠️ The old version ({old_version}) has known internal incidents that may be resolved in the new version.")
    
    if new_incidents:
        risk_reasoning.append(f"⚠️ WARNING: The new version ({new_version}) has known internal incidents. Consider investigating before upgrading.")
    
    # Security reasoning
    security_reasoning = []
    if old_security_issues:
        security_reasoning.append(f"🔒 The old version ({old_version}) has known security vulnerabilities: {', '.join(old_security_issues)}")
        if not new_security_issues:
            security_reasoning.append(f"✅ The new version ({new_version}) appears to address these security issues.")
    else:
        security_reasoning.append(f"✅ No known security issues found for version {old_version}.")
    
    if new_security_issues:
        security_reasoning.append(f"⚠️ WARNING: The new version ({new_version}) has known security issues: {', '.join(new_security_issues)}")
    
    # Compatibility reasoning
    compatibility_reasoning = []
    if compat_info["compatible"]:
        compatibility_reasoning.append(f"✅ Compatible versions found: {', '.join(compat_info['compatible'])}")
    if compat_info["incompatible"]:
        compatibility_reasoning.append(f"⚠️ Potential compatibility concerns: {', '.join(compat_info['incompatible'])}")
    if not compat_info["compatible"] and not compat_info["incompatible"]:
        compatibility_reasoning.append(f"ℹ️ No compatibility data found for other services using {package}.")
    
    return {
        "summary": summary,
        "risk_reasoning": risk_reasoning,
        "security_reasoning": security_reasoning,
        "compatibility_reasoning": compatibility_reasoning,
        "release_notes": release_notes,
        "bump_type": bump_type,
        "sources": sources
    }

# ============================================================================
# STREAMLIT UI
# ============================================================================

def format_explanation(explanation: Dict[str, Any]) -> str:
    """Format the explanation object into a natural language response."""
    lines = []
    
    # Summary
    lines.append(f"**Summary:** {explanation['summary']}")
    lines.append("")
    
    # Release notes
    lines.append(f"**Release Notes:** {explanation['release_notes']}")
    lines.append("")
    
    # Risk reasoning
    if explanation['risk_reasoning']:
        lines.append("**Risk Assessment:**")
        for reason in explanation['risk_reasoning']:
            lines.append(f"- {reason}")
        lines.append("")
    
    # Security reasoning
    if explanation['security_reasoning']:
        lines.append("**Security Considerations:**")
        for reason in explanation['security_reasoning']:
            lines.append(f"- {reason}")
        lines.append("")
    
    # Compatibility reasoning
    if explanation['compatibility_reasoning']:
        lines.append("**Compatibility:**")
        for reason in explanation['compatibility_reasoning']:
            lines.append(f"- {reason}")
        lines.append("")
    
    # Sources
    if explanation['sources']:
        lines.append("**Sources:**")
        for source in explanation['sources']:
            lines.append(f"- {source}")
    
    return "\n".join(lines)

def main():
    st.set_page_config(
        page_title="Dependency Reasoning Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Dependency Reasoning Chatbot")
    st.markdown("Analyze and reason about dependency upgrades across different ecosystems.")
    
    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Upgrade Details")
        
        ecosystem = st.selectbox(
            "Ecosystem",
            ["pip", "npm", "maven", "gradle", "cargo", "composer"],
            index=0
        )
        
        package = st.text_input(
            "Package Name",
            placeholder="e.g., auth-lib",
            value=""
        )
        
        col1, col2 = st.columns(2)
        with col1:
            old_version = st.text_input(
                "Old Version",
                placeholder="e.g., 2.1.0",
                value=""
            )
        with col2:
            new_version = st.text_input(
                "New Version",
                placeholder="e.g., 2.2.0",
                value=""
            )
        
        context = st.text_input(
            "Context (Optional)",
            placeholder="e.g., Checkout Service, prod rollout",
            value=""
        )
        
        explain_button = st.button(
            "🔍 Explain this upgrade",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("### 📦 Example Packages")
        st.markdown("Try these examples:")
        st.code("auth-lib: 2.1.0 → 2.2.0")
        st.code("payments-core: 3.1.0 → 3.2.0")
        st.code("logging-lib: 1.5.0 → 1.5.1")
    
    # Main chat area
    st.header("💬 Conversation")
    
    # Display existing messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])
    
    # Handle button click
    if explain_button:
        if not package or not old_version or not new_version:
            st.error("Please fill in package name, old version, and new version.")
        else:
            # Add user message
            user_query = f"Explain upgrading {package} from {old_version} to {new_version}"
            if context:
                user_query += f" (Context: {context})"
            
            st.session_state.messages.append({
                "role": "user",
                "content": user_query
            })
            
            # Generate explanation
            try:
                explanation = explain_version_choice(
                    package=package,
                    old_version=old_version,
                    new_version=new_version,
                    ecosystem=ecosystem,
                    context=context if context else None
                )
                
                formatted_response = format_explanation(explanation)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": formatted_response
                })
                
                # Rerun to show new messages
                st.rerun()
                
            except Exception as e:
                error_msg = f"Error generating explanation: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.rerun()
    
    # Clear conversation button
    if st.session_state.messages:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()

