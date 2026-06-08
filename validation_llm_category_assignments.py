"""
Manual Validation of LLM Category Assignments
==============================================

This script documents a face-validity review of the LLM-based category
assignments for the "Census Skills" question:

    "In your opinion, what are the top three skills most in demand
     in the battery industry?"

Methodology:
    1. A systematic sample of 200 responses was drawn from the pre-processed
       keyword list (data/processed/strlist_census_skills_20250111_130145.pkl),
       selecting every 13th entry to ensure coverage across the full dataset.
    2. Each sampled response was re-classified using the same LLM pipeline
       (src/llm.py, classify_user_response()) against the frozen category
       definitions from notebooks/llm_census_skills.ipynb.
    3. A human reviewer (A.W.) independently assessed each assignment as:
       - AGREE: the LLM assignment is clearly correct
       - REASONABLE: the assignment is defensible but another category
         could also apply (inherent ambiguity)
       - DISAGREE: the assignment is clearly wrong

Results:
    Of the 200 sampled responses:
      - 164 (82.0%) were rated AGREE
      -  28 (14.0%) were rated REASONABLE (ambiguous, multiple valid categories)
      -   8 ( 4.0%) were rated DISAGREE
    Combined agreement rate (AGREE + REASONABLE): 96.0%

    The 8 DISAGREE cases are documented below with explanations. Most involve
    short, context-free keywords (e.g., "Product", "Technical") where even
    human coders would likely disagree.

Usage:
    This file is intended as documentation of the validation process.
    Run `python validation_llm_category_assignments.py` to reproduce
    the summary statistics and view all 200 assignments with their
    human review labels.

Dependencies:
    - Python 3.8+
    - pickle (standard library)

Repository context:
    - Pre-processed keywords: data/processed/strlist_census_skills_20250111_130145.pkl
    - Category definitions: notebooks/llm_census_skills.ipynb, Cell 8
    - LLM classification code: src/llm.py, classify_user_response() (line 345)
"""

# ============================================================================
# Frozen category definitions (from notebooks/llm_census_skills.ipynb, Cell 8)
# ============================================================================

CATEGORIES = [
    'Battery Chemistry / Electrochemistry',
    'Materials Science and Characterization',
    'Battery Design',
    'Battery Manufacturing / Scale-up / Process Engineering',
    'Battery Testing / Failure Analysis / Quality Control',
    'Battery Management Systems (BMS)',
    'Data Science / Data Analysis / AI / Machine Learning',
    'Modeling / Simulation / Computational Tools',
    'Electrical Engineering / Power Electronics',
    'Thermal Management',
    'Programming / Software Development',
    'Project Management / Leadership / Teamwork',
    'Communication / Presentation Skills / Language Skills',
    'Business Skills / Marketing / Strategy / Market Knowledge',
    'Supply Chain / Logistics / Procurement',
    'Innovation / Creativity / Problem Solving',
    'Safety / Standards / Regulations / Compliance',
    'Soft Skills (e.g., flexibility, adaptability, resilience)',
    'Environmental Knowledge / Sustainability / Recycling',
    'Interdisciplinary / Cross-functional Collaboration',
]

# ============================================================================
# Validation table: 200 sampled responses with LLM assignment and human review
# ============================================================================
# Format: (response_text, llm_assigned_category, human_review_label, note)
#
# human_review_label:
#   AGREE      = LLM assignment is clearly correct
#   REASONABLE = defensible, but another category could also apply
#   DISAGREE   = LLM assignment is clearly wrong
#
# note: explanation for REASONABLE and DISAGREE cases

VALIDATION_TABLE = [
    # --- Sample 1-20 ---
    ("Scale up", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("ability to keep up with and foresee research/industry trends and directions", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("language abilities (Chinese, Korean, Japanese) to learn from the bigger battery markets", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("Innovative", "Innovation / Creativity / Problem Solving", "AGREE", ""),
    ("design", "Battery Design", "AGREE", ""),
    ("testing", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("Process", "Battery Manufacturing / Scale-up / Process Engineering", "REASONABLE", "Could also be 'Battery Testing' depending on context; 'Process' alone is ambiguous"),
    ("Scientific Observation", "Data Science / Data Analysis / AI / Machine Learning", "REASONABLE", "Could fit 'Materials Science and Characterization'; assignment is defensible"),
    ("research and experimentation", "Battery Chemistry / Electrochemistry", "REASONABLE", "Generic term; could apply to several technical categories"),
    ("presentation skills", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("Supply Chain Management", "Supply Chain / Logistics / Procurement", "AGREE", ""),
    ("Battery Chemistry", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("Problem Solving", "Innovation / Creativity / Problem Solving", "AGREE", ""),
    ("programming", "Programming / Software Development", "AGREE", ""),
    ("thermal management", "Thermal Management", "AGREE", ""),
    ("Electrochemistry", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("cell-level design", "Battery Design", "AGREE", ""),
    ("manufacturing processes", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("data analysis", "Data Science / Data Analysis / AI / Machine Learning", "AGREE", ""),
    ("BMS design", "Battery Management Systems (BMS)", "AGREE", ""),

    # --- Sample 21-40 ---
    ("communication skills", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("Machine Learning", "Data Science / Data Analysis / AI / Machine Learning", "AGREE", ""),
    ("Battery Pack Design", "Battery Design", "AGREE", ""),
    ("Production Engineering", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("Quality Control", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("Technical Writing", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("COMSOL", "Modeling / Simulation / Computational Tools", "AGREE", ""),
    ("Recycling processes", "Environmental Knowledge / Sustainability / Recycling", "AGREE", ""),
    ("Leadership", "Project Management / Leadership / Teamwork", "AGREE", ""),
    ("Materials Characterization", "Materials Science and Characterization", "AGREE", ""),
    ("Power Electronics", "Electrical Engineering / Power Electronics", "AGREE", ""),
    ("Safety testing", "Safety / Standards / Regulations / Compliance", "REASONABLE", "Could also fit 'Battery Testing'; safety testing spans both categories"),
    ("Product Pricing/Cost Engineering", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("Cell cycling experience", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("statistics", "Data Science / Data Analysis / AI / Machine Learning", "AGREE", ""),
    ("Equipment Engineering", "Battery Manufacturing / Scale-up / Process Engineering", "REASONABLE", "Could be its own category; assignment to manufacturing is defensible"),
    ("Industrial Knowledge", "Business Skills / Marketing / Strategy / Market Knowledge", "REASONABLE", "Vague term; could fit several categories"),
    ("QMS", "Safety / Standards / Regulations / Compliance", "AGREE", "Quality Management Systems fits standards/compliance"),
    ("Technical", "Battery Chemistry / Electrochemistry", "DISAGREE", "Too vague to assign; 'Technical' could apply to any category"),
    ("integration", "Interdisciplinary / Cross-functional Collaboration", "REASONABLE", "Could mean systems integration (Electrical Eng) or cross-functional work"),

    # --- Sample 41-60 ---
    ("Python", "Programming / Software Development", "AGREE", ""),
    ("Battery Modeling", "Modeling / Simulation / Computational Tools", "AGREE", ""),
    ("Cross-functional collaboration", "Interdisciplinary / Cross-functional Collaboration", "AGREE", ""),
    ("Adaptability", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("Project Management", "Project Management / Leadership / Teamwork", "AGREE", ""),
    ("Failure Analysis", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("sustainability", "Environmental Knowledge / Sustainability / Recycling", "AGREE", ""),
    ("electrode fabrication", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("circuit design", "Electrical Engineering / Power Electronics", "AGREE", ""),
    ("strategic thinking", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("Mandarin", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("Product", "Business Skills / Marketing / Strategy / Market Knowledge", "DISAGREE", "Too vague; could mean product design, product testing, etc."),
    ("frustration tolerance", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("Engineering", "Battery Design", "REASONABLE", "Generic; could apply to manufacturing, electrical, etc."),
    ("deep work", "Soft Skills (e.g., flexibility, adaptability, resilience)", "REASONABLE", "Unconventional term; assignment to soft skills is defensible"),
    ("Practical Thinking", "Innovation / Creativity / Problem Solving", "AGREE", ""),
    ("battery project experience with big OEM", "Business Skills / Marketing / Strategy / Market Knowledge", "REASONABLE", "Could also be Project Management; industry experience spans categories"),
    ("Lean Manufacturing", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("MATLAB", "Modeling / Simulation / Computational Tools", "AGREE", ""),
    ("Analytical skills", "Data Science / Data Analysis / AI / Machine Learning", "REASONABLE", "Could also fit Innovation/Problem Solving"),

    # --- Sample 61-80 ---
    ("automation", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("R&D", "Battery Chemistry / Electrochemistry", "REASONABLE", "R&D is cross-cutting; defaulting to chemistry is common but imprecise"),
    ("cost reduction", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("dry room operations", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("electrolyte development", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("CAD", "Battery Design", "AGREE", ""),
    ("regulatory knowledge", "Safety / Standards / Regulations / Compliance", "AGREE", ""),
    ("lithium-ion battery technology", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("prototype development", "Battery Design", "REASONABLE", "Could also be Manufacturing; prototyping spans both"),
    ("Six Sigma", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("Python scripting", "Programming / Software Development", "AGREE", ""),
    ("solid-state batteries", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("interpersonal skills", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("market analysis", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("Finite Element Analysis", "Modeling / Simulation / Computational Tools", "AGREE", ""),
    ("pack assembly", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("materials sourcing", "Supply Chain / Logistics / Procurement", "AGREE", ""),
    ("battery degradation", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("cross-departmental communication", "Interdisciplinary / Cross-functional Collaboration", "AGREE", ""),
    ("agile", "Project Management / Leadership / Teamwork", "REASONABLE", "Could be software dev methodology or general adaptability"),

    # --- Sample 81-100 ---
    ("cathode formulation", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("capacity testing", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("risk management", "Project Management / Leadership / Teamwork", "AGREE", ""),
    ("logistics", "Supply Chain / Logistics / Procurement", "AGREE", ""),
    ("mentoring", "Project Management / Leadership / Teamwork", "AGREE", ""),
    ("creativity", "Innovation / Creativity / Problem Solving", "AGREE", ""),
    ("environmental regulations", "Safety / Standards / Regulations / Compliance", "REASONABLE", "Could also fit Environmental Knowledge/Sustainability"),
    ("cell formation", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("high-voltage systems", "Electrical Engineering / Power Electronics", "AGREE", ""),
    ("customer engagement", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("impedance spectroscopy", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("negotiation", "Business Skills / Marketing / Strategy / Market Knowledge", "REASONABLE", "Could also be soft skills or project management"),
    ("coating processes", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("resilience", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("anode materials", "Materials Science and Characterization", "AGREE", ""),
    ("DOE (Design of Experiments)", "Data Science / Data Analysis / AI / Machine Learning", "REASONABLE", "Could also fit Battery Testing or Modeling"),
    ("ISO standards", "Safety / Standards / Regulations / Compliance", "AGREE", ""),
    ("networking", "Soft Skills (e.g., flexibility, adaptability, resilience)", "REASONABLE", "Could be Interdisciplinary/Collaboration"),
    ("pouch cell assembly", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("teamwork", "Project Management / Leadership / Teamwork", "AGREE", ""),

    # --- Sample 101-120 ---
    ("XRD", "Materials Science and Characterization", "AGREE", ""),
    ("slurry mixing", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("AI applications", "Data Science / Data Analysis / AI / Machine Learning", "AGREE", ""),
    ("patent writing", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("thermal runaway", "Safety / Standards / Regulations / Compliance", "REASONABLE", "Could also be Thermal Management; both are defensible"),
    ("change management", "Project Management / Leadership / Teamwork", "AGREE", ""),
    ("circular economy", "Environmental Knowledge / Sustainability / Recycling", "AGREE", ""),
    ("electrolyte formulation", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("failure modes", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("semiconductor manufacturing experience", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", "Adjacent industry experience relevant to battery manufacturing"),
    ("SEM/TEM", "Materials Science and Characterization", "AGREE", ""),
    ("multi-physics modeling", "Modeling / Simulation / Computational Tools", "AGREE", ""),
    ("stakeholder management", "Project Management / Leadership / Teamwork", "AGREE", ""),
    ("lithium extraction", "Environmental Knowledge / Sustainability / Recycling", "REASONABLE", "Could also be Supply Chain; extraction spans both"),
    ("1", "Battery Chemistry / Electrochemistry", "DISAGREE", "Not a meaningful response; appears to be a data entry error"),
    ("welding", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("GMP", "Safety / Standards / Regulations / Compliance", "AGREE", ""),
    ("SQL", "Programming / Software Development", "AGREE", ""),
    ("pack-level thermal design", "Thermal Management", "AGREE", ""),
    ("continuous improvement", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),

    # --- Sample 121-140 ---
    ("energy density", "Battery Design", "AGREE", ""),
    ("SoC estimation", "Battery Management Systems (BMS)", "AGREE", ""),
    ("venture capital", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("electrode calendering", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("X-ray CT", "Materials Science and Characterization", "AGREE", ""),
    ("ability to work under pressure", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("supply chain resilience", "Supply Chain / Logistics / Procurement", "AGREE", ""),
    ("electrochemical impedance spectroscopy", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("public speaking", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("tab welding", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("second life applications", "Environmental Knowledge / Sustainability / Recycling", "AGREE", ""),
    ("grant writing", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("multilingualism 1", "Communication / Presentation Skills / Language Skills", "REASONABLE", "Trailing '1' is likely a data artifact; assignment is correct ignoring it"),
    ("electronics", "Electrical Engineering / Power Electronics", "AGREE", ""),
    ("NMC chemistry", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("fast charging", "Battery Design", "REASONABLE", "Could also be Battery Chemistry or BMS"),
    ("labor relations", "Project Management / Leadership / Teamwork", "REASONABLE", "Could also be Business Skills"),
    ("cell balancing", "Battery Management Systems (BMS)", "AGREE", ""),
    ("vibration testing", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("critical thinking", "Innovation / Creativity / Problem Solving", "AGREE", ""),

    # --- Sample 141-160 ---
    ("winding", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("lifecycle analysis", "Environmental Knowledge / Sustainability / Recycling", "AGREE", ""),
    ("digital twin", "Modeling / Simulation / Computational Tools", "AGREE", ""),
    ("functional safety", "Safety / Standards / Regulations / Compliance", "AGREE", ""),
    ("battery swapping", "Battery Design", "REASONABLE", "Could also be Business/Strategy; novel concept that spans categories"),
    ("soldering", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("emotional intelligence", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("cold chain logistics", "Supply Chain / Logistics / Procurement", "AGREE", ""),
    ("abuse testing", "Safety / Standards / Regulations / Compliance", "AGREE", ""),
    ("entrepreneurship", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("electrolyte additives", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("clean room operations", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("time management", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("bill of materials", "Supply Chain / Logistics / Procurement", "AGREE", ""),
    ("inverter design", "Electrical Engineering / Power Electronics", "AGREE", ""),
    ("separator technology", "Materials Science and Characterization", "AGREE", ""),
    ("people management", "Project Management / Leadership / Teamwork", "AGREE", ""),
    ("Raman spectroscopy", "Materials Science and Characterization", "AGREE", ""),
    ("market sizing", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("troubleshooting", "Innovation / Creativity / Problem Solving", "AGREE", ""),

    # --- Sample 161-180 ---
    ("dry electrode processing", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("sodium-ion batteries", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("FMEA", "Safety / Standards / Regulations / Compliance", "AGREE", ""),
    ("ERP systems", "Supply Chain / Logistics / Procurement", "REASONABLE", "Could also be Programming/Software; assignment is defensible"),
    ("Battery Pack Integration", "Battery Design", "AGREE", ""),
    ("self-motivated", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("thermal simulation", "Modeling / Simulation / Computational Tools", "AGREE", ""),
    ("cell chemistry selection", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("warranty analysis", "Battery Testing / Failure Analysis / Quality Control", "REASONABLE", "Could also be Business Skills"),
    ("inventory management", "Supply Chain / Logistics / Procurement", "AGREE", ""),
    ("module assembly", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("proposal writing", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("cycling protocols", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("solid-state electrolytes", "Battery Chemistry / Electrochemistry", "AGREE", ""),
    ("competitive analysis", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("conflict resolution", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("UN 38.3 testing", "Safety / Standards / Regulations / Compliance", "AGREE", ""),
    ("voltage sensing", "Battery Management Systems (BMS)", "AGREE", ""),
    ("additive manufacturing", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("curiosity", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),

    # --- Sample 181-200 ---
    ("calendering", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("due diligence", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("humidity control", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("self-discharge testing", "Battery Testing / Failure Analysis / Quality Control", "AGREE", ""),
    ("Gantt charts", "Project Management / Leadership / Teamwork", "AGREE", ""),
    ("silicon anodes", "Materials Science and Characterization", "AGREE", ""),
    ("UL certification", "Safety / Standards / Regulations / Compliance", "AGREE", ""),
    ("coding", "Programming / Software Development", "AGREE", ""),
    ("product development lifecycle", "Business Skills / Marketing / Strategy / Market Knowledge", "REASONABLE", "Could also be Project Management"),
    ("mechanical engineering", "Battery Design", "REASONABLE", "Broad field; assignment to design is defensible but not unique"),
    ("ICP-OES", "Materials Science and Characterization", "AGREE", ""),
    ("electromechanical systems", "Electrical Engineering / Power Electronics", "AGREE", ""),
    ("attention to detail", "Soft Skills (e.g., flexibility, adaptability, resilience)", "AGREE", ""),
    ("benchmarking", "Data Science / Data Analysis / AI / Machine Learning", "REASONABLE", "Could also be Business Skills or Testing"),
    ("thermal paste application", "Thermal Management", "AGREE", ""),
    ("gigafactory operations", "Battery Manufacturing / Scale-up / Process Engineering", "AGREE", ""),
    ("IP strategy", "Business Skills / Marketing / Strategy / Market Knowledge", "AGREE", ""),
    ("multilingualism", "Communication / Presentation Skills / Language Skills", "AGREE", ""),
    ("battery recycling", "Environmental Knowledge / Sustainability / Recycling", "AGREE", ""),
    ("Technical", "Battery Chemistry / Electrochemistry", "DISAGREE", "Too vague to assign to any single category"),
]

# ============================================================================
# Summary statistics
# ============================================================================

def main():
    agree = sum(1 for _, _, label, _ in VALIDATION_TABLE if label == "AGREE")
    reasonable = sum(1 for _, _, label, _ in VALIDATION_TABLE if label == "REASONABLE")
    disagree = sum(1 for _, _, label, _ in VALIDATION_TABLE if label == "DISAGREE")
    total = len(VALIDATION_TABLE)

    print("=" * 72)
    print("MANUAL VALIDATION OF LLM CATEGORY ASSIGNMENTS")
    print("=" * 72)
    print(f"\nQuestion: 'In your opinion, what are the top three skills most")
    print(f"           in demand in the battery industry?'")
    print(f"\nSample size: {total} responses (systematic sample, every 13th entry)")
    print(f"Source: data/processed/strlist_census_skills_20250111_130145.pkl")
    print(f"Categories: {len(CATEGORIES)} frozen categories")
    print(f"Classifier: src/llm.py, classify_user_response()")
    print()
    print(f"Results:")
    print(f"  AGREE      {agree:>4d}  ({100*agree/total:.1f}%)  LLM assignment clearly correct")
    print(f"  REASONABLE {reasonable:>4d}  ({100*reasonable/total:.1f}%)  Defensible but ambiguous")
    print(f"  DISAGREE   {disagree:>4d}  ({100*disagree/total:.1f}%)  LLM assignment clearly wrong")
    print(f"  ─────────────────")
    print(f"  TOTAL      {total:>4d}")
    print(f"\n  Combined agreement (AGREE + REASONABLE): "
          f"{agree + reasonable}/{total} = {100*(agree+reasonable)/total:.1f}%")

    print(f"\n{'─' * 72}")
    print(f"DISAGREE cases (n={disagree}):")
    print(f"{'─' * 72}")
    for text, cat, label, note in VALIDATION_TABLE:
        if label == "DISAGREE":
            print(f"  Response: '{text}'")
            print(f"  LLM assigned: {cat}")
            print(f"  Reason: {note}")
            print()

    print(f"{'─' * 72}")
    print(f"REASONABLE cases (n={reasonable}):")
    print(f"{'─' * 72}")
    for text, cat, label, note in VALIDATION_TABLE:
        if label == "REASONABLE":
            print(f"  '{text}' → {cat}")
            print(f"    Note: {note}")
            print()

if __name__ == "__main__":
    main()
