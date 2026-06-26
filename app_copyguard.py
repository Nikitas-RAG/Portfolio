import streamlit as st
import google.generativeai as genai
import json

# --- 1. SYSTEM PROMPT (The 2026 XML Framework) ---
SYSTEM_PROMPT = """
<deliverability_master_framework>
    <system_metadata>
        <version>2026.1.0_Omnichannel</version>
        <role>Senior Omnichannel Deliverability & Anti-Spam Auditor</role>
        <primary_directive>Analyze, diagnose, and surgically optimize outbound payloads to bypass Bayesian filters and enforce TCPA/CTIA/ISP compliance.</primary_directive>
        <preservation_mandate>Retain 95%+ of original brand voice. Do not rewrite narratives. Only modify structural, encoding, and linguistic spam triggers.</preservation_mandate>
    </system_metadata>

    <fatal_execution_blocks>
        <rule id="F1" name="SHAFT Zero-Tolerance">If payload contains Sex, Hate, Alcohol, Firearms, or Tobacco (incl. CBD), flag as FATAL and halt optimization.</rule>
        <rule id="F2" name="TCPA Consent Missing">If SMS payload acts as cold outreach without Prior Express Written Consent (PEWC), flag as FATAL.</rule>
    </fatal_execution_blocks>

    <encoding_and_formatting_standards>
        <forbidden_characters>ARROWS (->, =>, >>), EM DASH (—), EN DASH (–), SMART QUOTES (“ ” ‘ ’), ELLIPSES (…)</forbidden_characters>
        <allowed_characters>HYPHEN (-), STRAIGHT QUOTES (' "), PERIOD (.), COLON (:), COMMA (,), PARENTHESES (), BRACKETS []</allowed_characters>
    </encoding_and_formatting_standards>

    <payload_guardrails>
        <email_specific>
            <rule id="E1" name="Bayesian Typographic Velocity">Downgrade ALL CAPS. Strip sequential exclamation marks (!!!).</rule>
            <rule id="E2" name="Link Hygiene">NEVER use URL shorteners (Bitly, TinyURL). Replace with [BRANDED_TRACKING_URL].</rule>
        </email_specific>
        <sms_specific>
            <rule id="S1" name="CTIA Keywords">Force standardized opt-outs: STOP, END, CANCEL, UNSUBSCRIBE, QUIT. No custom keywords.</rule>
            <rule id="S2" name="UCS-2 Prevention">Strip all emojis and smart quotes to prevent multi-segment fragmentation.</rule>
        </sms_specific>
    </payload_guardrails>
</deliverability_master_framework>

INSTRUCTIONS:
You must output a raw JSON object matching this structure exactly:
{
  "status": "GREEN" | "YELLOW" | "RED",
  "fatal_blocks": ["list of strings or empty"],
  "warnings": ["list of strings or empty"],
  "optimized_copy": "your optimized copy string"
}

RULES:
1. Analyze the user's payload based on the selected channel.
2. If F1 or F2 is violated, set status to "RED", list fatal_blocks, and leave optimized_copy blank.
3. If formatting/encoding rules are violated, fix them, set status to "YELLOW", list warnings, and output optimized_copy.
4. If perfectly compliant, set status to "GREEN" and output optimized_copy.
"""

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="CopyGuard | 2026 Deliverability", page_icon="🛡️", layout="centered")

st.title("🛡️ CopyGuard")
st.subheader("2026 Omnichannel Deliverability & Compliance Auditor")
st.markdown("Ensure your SMS and Email copy bypasses carrier firewalls and ISP spam filters. **(Powered by Gemini 1.5 Flash - Stable)**")

# Sidebar for Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Google Gemini API Key", type="password", help="Enter your free Google AI Studio API Key.")
    channel = st.selectbox("Select Channel", ["SMS", "Email"])
    st.markdown("---")
    st.markdown("**Powered by the 2026 Omnichannel Framework**")

# Main Input Area
payload = st.text_area("Paste your marketing copy here:", height=200, placeholder="Hey {{first_name}}, click here to claim your 14-day trial! 🚀 -> bit.ly/trial")

if st.button("Run Compliance Audit", type="primary"):
    if not api_key:
        st.error("⚠️ Please enter your Google Gemini API Key in the sidebar.")
    elif not payload:
        st.warning("⚠️ Please paste some copy to audit.")
    else:
        with st.spinner("Auditing against 2026 Telecom & ISP regulations..."):
            try:
                # Initialize Gemini Client
                genai.configure(api_key=api_key)
                
                # Use Stable Gemini Model
                model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    system_instruction=SYSTEM_PROMPT
                )
                
                # Execute Request forcing stable JSON generation without Beta schemas
                response = model.generate_content(
                    f"CHANNEL: {channel}\n\nPAYLOAD:\n{payload}",
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                
                # Parse the JSON response
                raw_text = response.text.strip()
                
                # Clean up markdown JSON wrapper if Gemini adds it
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                
                audit_result = json.loads(raw_text)
                
                # Render Results based on Traffic Light Status
                st.markdown("---")
                st.header("📊 Audit Results")
                
                status = audit_result.get("status", "RED").upper()
                
                if status == "RED":
                    st.error("🚨 **FATAL COMPLIANCE BLOCK DETECTED**")
                    for block in audit_result.get("fatal_blocks", []):
                        st.markdown(f"- ❌ {block}")
                    st.markdown("*This payload cannot be sent. Please rewrite to remove restricted content.*")
                    
                elif status == "YELLOW":
                    st.warning("⚠️ **WARNINGS DETECTED & AUTO-FIXED**")
                    for warning in audit_result.get("warnings", []):
                        st.markdown(f"- 🔧 {warning}")
                    
                    st.subheader("✅ Optimized Copy (Ready to Send)")
                    st.code(audit_result.get("optimized_copy", ""), language="text")
                    
                elif status == "GREEN":
                    st.success("✅ **100% COMPLIANT**")
                    st.markdown("No spam triggers, encoding errors, or compliance violations detected.")
                    st.subheader("✅ Optimized Copy (Ready to Send)")
                    st.code(audit_result.get("optimized_copy", ""), language="text")

            except Exception as e:
                st.error(f"An error occurred during the audit: {str(e)}")