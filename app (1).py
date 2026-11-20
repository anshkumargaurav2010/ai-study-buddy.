import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date, datetime
import plotly.express as px

st.set_page_config(
    page_title="AI Study Buddy | Class 12",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = Path("study_buddy_data")
DATA_DIR.mkdir(exist_ok=True)
PROGRESS_FILE = DATA_DIR / "quiz_progress.json"

st.markdown("""
<style>
    .main {background: #f7f8fc;}
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    .hero {
        padding: 1.5rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #172554, #4338ca);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 {color: white; margin-bottom: .2rem;}
    .hero p {color: #e0e7ff; margin-bottom: 0;}
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #e5e7eb;
        padding: 14px; border-radius: 14px;
    }
    .small-muted {color: #64748b; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_progress(records):
    PROGRESS_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

QUESTION_BANK = {
    "Physics": [
        {"q": "What is the SI unit of capacitance?", "options": ["Ohm", "Farad", "Henry", "Volt"], "answer": "Farad", "why": "Capacitance is measured in farads (F)."},
        {"q": "The time constant of an RC circuit is:", "options": ["R/C", "RC", "1/RC", "R + C"], "answer": "RC", "why": "The time constant is τ = R × C."},
        {"q": "Which law relates current, voltage and resistance?", "options": ["Faraday's law", "Ohm's law", "Gauss's law", "Coulomb's law"], "answer": "Ohm's law", "why": "Ohm's law states V = IR for an ohmic conductor under constant physical conditions."},
        {"q": "The SI unit of electric charge is:", "options": ["Ampere", "Coulomb", "Watt", "Tesla"], "answer": "Coulomb", "why": "Electric charge is measured in coulombs (C)."},
        {"q": "For a capacitor, charge is given by:", "options": ["Q = CV", "Q = C/V", "Q = V/C", "Q = IR"], "answer": "Q = CV", "why": "The relation between charge, capacitance and potential difference is Q = CV."}
    ],
    "Chemistry": [
        {"q": "The pH of a neutral solution at 25°C is:", "options": ["0", "7", "10", "14"], "answer": "7", "why": "At 25°C, a neutral aqueous solution has pH 7."},
        {"q": "The oxidation state of oxygen in most compounds is:", "options": ["+1", "-1", "-2", "+2"], "answer": "-2", "why": "Oxygen commonly has oxidation state −2, with exceptions such as peroxides."},
        {"q": "Which is the unit of molarity?", "options": ["mol kg⁻¹", "mol L⁻¹", "g L⁻¹", "kg mol⁻¹"], "answer": "mol L⁻¹", "why": "Molarity is moles of solute per litre of solution."},
        {"q": "A catalyst changes the:", "options": ["Equilibrium constant", "Activation energy", "Enthalpy change", "Products"], "answer": "Activation energy", "why": "A catalyst provides an alternative pathway with lower activation energy."},
        {"q": "Which bond involves sharing of electron pairs?", "options": ["Ionic", "Covalent", "Metallic", "Hydrogen"], "answer": "Covalent", "why": "Covalent bonds form when atoms share electron pairs."}
    ],
    "Mathematics": [
        {"q": "The derivative of x² is:", "options": ["x", "2x", "x³", "2"], "answer": "2x", "why": "Using the power rule, d(xⁿ)/dx = nxⁿ⁻¹."},
        {"q": "The value of sin²θ + cos²θ is:", "options": ["0", "1", "2", "tan θ"], "answer": "1", "why": "This is the fundamental Pythagorean trigonometric identity."},
        {"q": "The determinant of an identity matrix of order 2 is:", "options": ["0", "1", "2", "4"], "answer": "1", "why": "The determinant of every identity matrix is 1."},
        {"q": "The integral of 1/x is:", "options": ["x²/2 + C", "ln|x| + C", "eˣ + C", "1/x² + C"], "answer": "ln|x| + C", "why": "The antiderivative of 1/x is ln|x| + C."},
        {"q": "If two events are independent, then P(A ∩ B) equals:", "options": ["P(A)+P(B)", "P(A)P(B)", "P(A)/P(B)", "0"], "answer": "P(A)P(B)", "why": "For independent events, the probability of both is the product of their probabilities."}
    ],
    "Biology": [
        {"q": "Which organelle is known as the powerhouse of the cell?", "options": ["Nucleus", "Ribosome", "Mitochondrion", "Golgi body"], "answer": "Mitochondrion", "why": "Mitochondria produce most ATP during aerobic respiration."},
        {"q": "DNA stands for:", "options": ["Deoxyribonucleic acid", "Ribonuclear acid", "Dinucleic acid", "Deoxyribose nitrogen acid"], "answer": "Deoxyribonucleic acid", "why": "DNA is deoxyribonucleic acid."},
        {"q": "The functional unit of the kidney is:", "options": ["Neuron", "Nephron", "Alveolus", "Villus"], "answer": "Nephron", "why": "Nephrons filter blood and help form urine."},
        {"q": "Which blood cells help in clotting?", "options": ["Red blood cells", "White blood cells", "Platelets", "Plasma"], "answer": "Platelets", "why": "Platelets help form clots to reduce blood loss."},
        {"q": "Photosynthesis mainly occurs in:", "options": ["Mitochondria", "Chloroplasts", "Nucleus", "Lysosomes"], "answer": "Chloroplasts", "why": "Chloroplasts contain chlorophyll and host photosynthesis."}
    ],
    "Computer Science": [
        {"q": "Which Python data type stores key-value pairs?", "options": ["List", "Tuple", "Dictionary", "Set"], "answer": "Dictionary", "why": "A Python dictionary maps keys to values."},
        {"q": "Which keyword defines a function in Python?", "options": ["func", "define", "def", "function"], "answer": "def", "why": "Python functions are declared using def."},
        {"q": "Which SQL command retrieves data?", "options": ["GET", "SELECT", "FETCHALL", "OPEN"], "answer": "SELECT", "why": "SELECT retrieves rows from database tables."},
        {"q": "Which structure follows FIFO?", "options": ["Stack", "Queue", "Tree", "Graph"], "answer": "Queue", "why": "A queue follows first-in, first-out order."},
        {"q": "What does CSV stand for?", "options": ["Computer Saved Values", "Comma-Separated Values", "Column Stored Variable", "Common System Version"], "answer": "Comma-Separated Values", "why": "CSV is a plain-text tabular data format."}
    ]
}


# 20 additional Class 12 practice questions for each of the four core subjects.
# Format: question, options, correct answer, explanation, difficulty
EXTRA_QUESTIONS = {
    "Physics": [
        ("The electric field inside a conductor in electrostatic equilibrium is:", ["Zero", "Maximum", "Infinite", "Always non-zero"], "Zero", "Free charges rearrange until the internal electrostatic field is zero.", "Easy"),
        ("The SI unit of electric potential is:", ["Coulomb", "Volt", "Farad", "Newton"], "Volt", "Potential difference is measured in volts (V).", "Easy"),
        ("Two equal positive charges are separated by distance r. If the distance is doubled, the force becomes:", ["Four times", "Twice", "Half", "One-fourth"], "One-fourth", "Coulomb's law gives force proportional to 1/r².", "Easy"),
        ("The equivalent capacitance of capacitors connected in parallel is:", ["The sum of capacitances", "The reciprocal sum", "Always less than the smallest", "The product divided by sum"], "The sum of capacitances", "For parallel capacitors, C_eq = C₁ + C₂ + ...", "Easy"),
        ("Which material is commonly used as a semiconductor?", ["Copper", "Silicon", "Aluminium", "Silver"], "Silicon", "Silicon is a widely used elemental semiconductor.", "Easy"),
        ("The direction of conventional current is:", ["Direction of electron drift", "Opposite to electron drift", "Always upward", "Random"], "Opposite to electron drift", "Conventional current is defined in the direction positive charge would move.", "Medium"),
        ("The resistance of a wire is doubled if its length is doubled and area remains the same. This follows from:", ["R = ρA/L", "R = ρL/A", "R = L/A²", "R = ρLA"], "R = ρL/A", "Resistance is directly proportional to length and inversely proportional to area.", "Medium"),
        ("The magnetic field at the centre of a circular current loop is proportional to:", ["Current", "Square of current", "Inverse of current", "Resistance only"], "Current", "For a fixed radius, B = μ₀I/(2R), so B is proportional to I.", "Medium"),
        ("A charged particle moving parallel to a uniform magnetic field experiences magnetic force:", ["qvB", "Zero", "qB/v", "Maximum"], "Zero", "F = qvB sin θ; for parallel motion θ = 0°.", "Easy"),
        ("The SI unit of magnetic flux is:", ["Tesla", "Weber", "Henry", "Ampere"], "Weber", "Magnetic flux is measured in webers (Wb).", "Easy"),
        ("Lenz's law is consistent with conservation of:", ["Charge", "Energy", "Mass only", "Momentum only"], "Energy", "The induced current opposes the change that produces it, in accordance with energy conservation.", "Medium"),
        ("The rms value of an alternating voltage with peak value V₀ is:", ["V₀", "V₀/2", "V₀/√2", "√2V₀"], "V₀/√2", "For a sinusoidal AC voltage, V_rms = V₀/√2.", "Medium"),
        ("In a series LCR circuit at resonance, the impedance is:", ["Zero", "R", "XL + XC", "Infinite"], "R", "At resonance, inductive and capacitive reactances cancel.", "Medium"),
        ("The phenomenon responsible for the blue colour of the sky is:", ["Reflection", "Refraction", "Scattering", "Interference"], "Scattering", "Shorter wavelengths of sunlight are scattered more strongly by air molecules.", "Easy"),
        ("The power of a lens of focal length 0.5 m is:", ["0.5 D", "1 D", "2 D", "5 D"], "2 D", "Lens power P = 1/f when f is in metres, so P = 1/0.5 = 2 D.", "Medium"),
        ("In Young's double-slit experiment, fringe width increases when:", ["Wavelength decreases", "Slit separation increases", "Screen distance increases", "Both slits are closed"], "Screen distance increases", "Fringe width β = λD/d, so it increases with D.", "Medium"),
        ("The energy of a photon is given by:", ["mc²", "hν", "½mv²", "qV²"], "hν", "Planck's relation gives photon energy E = hν.", "Easy"),
        ("In the photoelectric effect, the stopping potential depends on:", ["Intensity only", "Frequency of incident light", "Area of metal only", "Distance from source only"], "Frequency of incident light", "Maximum kinetic energy, and hence stopping potential, depends on frequency above threshold.", "Medium"),
        ("A p-n junction diode is usually used as a:", ["Rectifier", "Transformer", "Capacitor", "Inductor"], "Rectifier", "A diode conducts mainly in one direction and can convert AC into pulsating DC.", "Easy"),
        ("The de Broglie wavelength of a particle is:", ["h/p", "hp", "p/h", "hE"], "h/p", "The matter-wave wavelength is λ = h/p, where p is momentum.", "Hard"),
    ],
    "Chemistry": [
        ("The number of particles present in one mole is approximately:", ["6.022 × 10²³", "3.0 × 10⁸", "9.8", "1.6 × 10⁻¹⁹"], "6.022 × 10²³", "Avogadro's constant is approximately 6.022 × 10²³ mol⁻¹.", "Easy"),
        ("Which colligative property is used to determine molar masses of polymers?", ["Osmotic pressure", "Surface tension", "Viscosity only", "Colour"], "Osmotic pressure", "Osmotic pressure can be measured at room temperature and is useful for large molar masses.", "Medium"),
        ("For an ideal solution, the enthalpy of mixing is:", ["Positive", "Negative", "Zero", "Infinite"], "Zero", "An ideal solution has ΔH_mix = 0.", "Medium"),
        ("The unit of rate constant for a first-order reaction is:", ["mol L⁻¹ s⁻¹", "s⁻¹", "L mol⁻¹ s⁻¹", "mol² L⁻²"], "s⁻¹", "For a first-order reaction, rate constant has dimensions of inverse time.", "Medium"),
        ("A catalyst increases reaction rate by:", ["Increasing ΔH", "Lowering activation energy", "Changing equilibrium constant", "Increasing product energy"], "Lowering activation energy", "A catalyst offers an alternative pathway with lower activation energy.", "Easy"),
        ("Which of the following is a strong electrolyte in water?", ["Glucose", "Urea", "Sodium chloride", "Ethanol"], "Sodium chloride", "NaCl dissociates extensively into ions in aqueous solution.", "Easy"),
        ("The standard electrode potential of the standard hydrogen electrode is:", ["1.00 V", "0.00 V", "−1.00 V", "0.76 V"], "0.00 V", "The standard hydrogen electrode is assigned zero volts by convention.", "Medium"),
        ("In a galvanic cell, oxidation occurs at the:", ["Cathode", "Anode", "Salt bridge", "Electrolyte surface only"], "Anode", "Oxidation occurs at the anode; reduction occurs at the cathode.", "Easy"),
        ("Which transition metal ion is generally colourless due to a d⁰ configuration?", ["Ti⁴⁺", "Cu²⁺", "Ni²⁺", "Co²⁺"], "Ti⁴⁺", "Ti⁴⁺ has an empty d subshell, so d-d transitions are not possible.", "Hard"),
        ("The coordination number of cobalt in [Co(NH₃)₆]³⁺ is:", ["3", "4", "6", "2"], "6", "Six ammonia ligands are directly bonded to the central cobalt ion.", "Easy"),
        ("Which ligand is bidentate?", ["NH₃", "H₂O", "Ethylenediamine", "Cl⁻"], "Ethylenediamine", "Ethylenediamine can coordinate through two donor nitrogen atoms.", "Medium"),
        ("The IUPAC name of CH₃CH₂OH is:", ["Methanol", "Ethanol", "Propanol", "Ethanal"], "Ethanol", "The two-carbon alcohol is named ethanol.", "Easy"),
        ("Which reagent is commonly used to distinguish aldehydes from ketones?", ["Tollens' reagent", "NaCl solution", "Dilute HCl", "Bromine water only"], "Tollens' reagent", "Aldehydes generally give a silver mirror with Tollens' reagent; ordinary ketones do not.", "Medium"),
        ("The functional group present in carboxylic acids is:", ["−CHO", "−COOH", "−OH", "−O−"], "−COOH", "Carboxylic acids contain the carboxyl group, −COOH.", "Easy"),
        ("Which polymer is formed by addition polymerisation of ethene?", ["Nylon-6,6", "Bakelite", "Polyethene", "Terylene"], "Polyethene", "Ethene molecules add together to form polyethene.", "Easy"),
        ("The monomers of proteins are:", ["Nucleotides", "Amino acids", "Monosaccharides", "Fatty acids"], "Amino acids", "Proteins are polymers made from amino acid units.", "Easy"),
        ("Which vitamin is water-soluble?", ["Vitamin A", "Vitamin D", "Vitamin E", "Vitamin C"], "Vitamin C", "Vitamin C is water-soluble; A, D and E are fat-soluble.", "Easy"),
        ("For a zero-order reaction, the half-life is proportional to:", ["Initial concentration", "Square of initial concentration", "Inverse of initial concentration", "Independent of concentration"], "Initial concentration", "For zero order, t₁/₂ = [A]₀/(2k).", "Hard"),
        ("The shape of [Ni(CN)₄]²⁻ is generally:", ["Tetrahedral", "Square planar", "Octahedral", "Linear"], "Square planar", "Ni(II) is d⁸ and CN⁻ is a strong-field ligand; the complex is square planar.", "Hard"),
        ("Which process converts an alkyl halide into an alcohol using aqueous KOH?", ["Substitution", "Addition", "Elimination only", "Polymerisation"], "Substitution", "Aqueous hydroxide replaces the halide ion with an −OH group.", "Medium"),
    ],
    "Mathematics": [
        ("The derivative of sin x with respect to x is:", ["−cos x", "cos x", "tan x", "−sin x"], "cos x", "The standard derivative is d(sin x)/dx = cos x.", "Easy"),
        ("The derivative of eˣ is:", ["xeˣ", "eˣ", "ln x", "1/x"], "eˣ", "The exponential function eˣ is its own derivative.", "Easy"),
        ("The value of ∫ cos x dx is:", ["−sin x + C", "sin x + C", "cos x + C", "tan x + C"], "sin x + C", "The antiderivative of cos x is sin x + C.", "Easy"),
        ("If A is a square matrix and |A| = 0, then A is:", ["Invertible", "Singular", "Identity", "Diagonal with non-zero entries"], "Singular", "A matrix with zero determinant has no inverse and is called singular.", "Medium"),
        ("The order of a matrix with 3 rows and 2 columns is:", ["2 × 3", "3 × 2", "3 × 3", "2 × 2"], "3 × 2", "Matrix order is written as rows × columns.", "Easy"),
        ("The principal value of sin⁻¹(1) is:", ["0", "π/2", "π", "−π/2"], "π/2", "The principal range of inverse sine is [−π/2, π/2].", "Easy"),
        ("If f'(x) is positive on an interval, f is:", ["Decreasing", "Increasing", "Constant", "Discontinuous"], "Increasing", "A positive derivative indicates the function is increasing on that interval.", "Medium"),
        ("The slope of the tangent to y = x² at x = 3 is:", ["3", "6", "9", "12"], "6", "dy/dx = 2x, so at x = 3 the slope is 6.", "Easy"),
        ("The value of ∫₀¹ 2x dx is:", ["0", "1", "2", "4"], "1", "The integral is [x²]₀¹ = 1.", "Medium"),
        ("The distance between points (0, 0) and (3, 4) is:", ["3", "4", "5", "7"], "5", "Distance = √(3² + 4²) = 5.", "Easy"),
        ("A vector perpendicular to both i and j is along:", ["i", "j", "k", "i + j"], "k", "The unit vector k is perpendicular to both i and j.", "Medium"),
        ("The dot product of two perpendicular vectors is:", ["1", "−1", "0", "Their magnitudes multiplied"], "0", "a·b = |a||b|cos 90° = 0.", "Easy"),
        ("The probability of an impossible event is:", ["0", "1", "1/2", "−1"], "0", "An impossible event has probability zero.", "Easy"),
        ("If P(A) = 0.4 and P(B) = 0.5 for independent events, P(A ∩ B) is:", ["0.9", "0.2", "0.1", "0.4"], "0.2", "For independent events, P(A ∩ B) = P(A)P(B) = 0.4 × 0.5.", "Medium"),
        ("The maximum value of sin x for real x is:", ["−1", "0", "1", "2"], "1", "The sine function ranges from −1 to 1.", "Easy"),
        ("If a function is continuous at x = a, then:", ["Left limit and right limit differ", "Limit equals f(a)", "f(a) must be zero", "Derivative must be infinite"], "Limit equals f(a)", "Continuity requires lim(x→a) f(x) = f(a).", "Medium"),
        ("The inverse of a 2 × 2 matrix exists when its determinant is:", ["Zero", "Non-zero", "One only", "Negative only"], "Non-zero", "A square matrix is invertible exactly when its determinant is non-zero.", "Medium"),
        ("The solution of dy/dx = 0 is:", ["y = x + C", "y = C", "y = eˣ", "y = x²"], "y = C", "A function with zero derivative is constant on an interval.", "Medium"),
        ("The area under y = x from x = 0 to x = 2 is:", ["1", "2", "3", "4"], "2", "Area = ∫₀² x dx = [x²/2]₀² = 2.", "Medium"),
        ("For vectors a and b, |a × b| equals:", ["|a||b| cos θ", "|a||b| sin θ", "a·b", "0 always"], "|a||b| sin θ", "The magnitude of the cross product is the product of magnitudes times sin of the angle.", "Hard"),
    ],
    "Biology": [
        ("The site of fertilisation in humans is usually the:", ["Uterus", "Ampullary-isthmic junction", "Cervix", "Vagina"], "Ampullary-isthmic junction", "Fertilisation commonly occurs at the ampullary-isthmic junction of the oviduct.", "Medium"),
        ("The hormone that triggers ovulation is:", ["FSH", "LH", "Progesterone", "Prolactin"], "LH", "A surge in luteinising hormone induces ovulation.", "Medium"),
        ("The male gamete in flowering plants is carried by the:", ["Sepal", "Pollen grain", "Ovule", "Stigma"], "Pollen grain", "Pollen grains carry the male gametophyte and deliver male gametes to the embryo sac.", "Easy"),
        ("The structure that connects the foetus to the placenta is the:", ["Oviduct", "Umbilical cord", "Cervix", "Amnion only"], "Umbilical cord", "The umbilical cord connects the foetus with the placenta.", "Easy"),
        ("Mendel performed his famous experiments on:", ["Maize", "Garden pea", "Fruit fly", "Bacteria"], "Garden pea", "Gregor Mendel used Pisum sativum, the garden pea plant.", "Easy"),
        ("A test cross is performed with an individual that is:", ["Homozygous dominant", "Homozygous recessive", "Heterozygous", "Always a hybrid"], "Homozygous recessive", "A test cross pairs the individual of unknown genotype with a homozygous recessive individual.", "Medium"),
        ("The enzyme that joins Okazaki fragments is:", ["DNA ligase", "Helicase", "Amylase", "RNA polymerase"], "DNA ligase", "DNA ligase seals the nicks between Okazaki fragments on the lagging strand.", "Medium"),
        ("The genetic material in most organisms is:", ["Protein", "DNA", "Lipid", "Carbohydrate"], "DNA", "DNA is the hereditary material in most organisms; some viruses use RNA.", "Easy"),
        ("The process by which RNA is synthesised from DNA is:", ["Translation", "Transcription", "Replication", "Mutation"], "Transcription", "Transcription uses a DNA template to synthesise RNA.", "Easy"),
        ("The codon AUG generally codes for:", ["Glycine", "Methionine", "Tryptophan", "Stop"], "Methionine", "AUG is the start codon and codes for methionine.", "Medium"),
        ("Which of these is an example of a restriction endonuclease?", ["EcoRI", "DNA ligase", "Cellulase", "Pepsin"], "EcoRI", "EcoRI recognises a specific DNA sequence and cuts DNA at or near that site.", "Medium"),
        ("PCR is used to:", ["Amplify DNA", "Translate proteins", "Destroy RNA", "Separate cells"], "Amplify DNA", "Polymerase chain reaction makes many copies of a selected DNA segment.", "Easy"),
        ("The first trophic level in a food chain is occupied by:", ["Carnivores", "Decomposers", "Producers", "Herbivores"], "Producers", "Producers convert solar or chemical energy into organic matter.", "Easy"),
        ("The pyramid of energy in an ecosystem is always:", ["Inverted", "Upright", "Spindle-shaped", "Absent"], "Upright", "Energy decreases at successive trophic levels, so the energy pyramid is always upright.", "Medium"),
        ("The major cause of ozone layer depletion is associated with:", ["CFCs", "Oxygen", "Nitrogen", "Water vapour"], "CFCs", "Chlorofluorocarbons release chlorine radicals that catalytically destroy ozone.", "Medium"),
        ("The term biodiversity refers to the variety of:", ["Only animals", "Life at genetic, species and ecosystem levels", "Only plants", "Only habitats"], "Life at genetic, species and ecosystem levels", "Biodiversity includes variation within species, between species and among ecosystems.", "Easy"),
        ("The antibody-producing cells are differentiated:", ["B-lymphocytes", "Red blood cells", "Platelets", "Neurons"], "B-lymphocytes", "Activated B-lymphocytes differentiate into plasma cells that secrete antibodies.", "Medium"),
        ("Which disease is caused by a protozoan?", ["Typhoid", "Malaria", "Tuberculosis", "Influenza"], "Malaria", "Malaria is caused by Plasmodium, a protozoan parasite.", "Easy"),
        ("In humans, the normal chromosome number in a somatic cell is:", ["23", "44", "46", "48"], "46", "Human somatic cells typically contain 23 pairs, or 46 chromosomes.", "Easy"),
        ("The theory of natural selection is associated with:", ["Gregor Mendel", "Charles Darwin", "Louis Pasteur", "Robert Hooke"], "Charles Darwin", "Darwin explained evolution through natural selection.", "Easy"),
    ],
}

for _subject, _items in EXTRA_QUESTIONS.items():
    for _q, _options, _answer, _why, _difficulty in _items:
        QUESTION_BANK[_subject].append({
            "q": _q,
            "options": _options,
            "answer": _answer,
            "why": _why,
            "difficulty": _difficulty,
        })

# Give the original sample questions a difficulty label too.
for _questions in QUESTION_BANK.values():
    for _question in _questions:
        _question.setdefault("difficulty", "Medium")

SUBJECTS = list(QUESTION_BANK.keys())

with st.sidebar:
    st.title("📚 Study Buddy")
    st.caption("Your Class 12 learning companion")
    page = st.radio(
        "NAVIGATION",
        ["🏠 Dashboard", "🧠 Take a Quiz", "📅 Study Planner", "📝 My Notes", "📈 Progress"]
    )
    st.divider()
    student_name = st.text_input("Student name", value=st.session_state.get("student_name", "Student"))
    st.session_state.student_name = student_name
    st.caption("Built with Python + Streamlit")

if page == "🏠 Dashboard":
    st.markdown(f"""
    <div class="hero">
      <h1>Welcome, {student_name or 'Student'}! 👋</h1>
      <p>Learn a little every day. Your next step starts here.</p>
    </div>
    """, unsafe_allow_html=True)

    records = st.session_state.progress
    total_quizzes = len(records)
    avg_score = sum(r["percentage"] for r in records) / total_quizzes if total_quizzes else 0
    best_score = max((r["percentage"] for r in records), default=0)

    c1, c2, c3 = st.columns(3)
    c1.metric("Quizzes completed", total_quizzes)
    c2.metric("Average score", f"{avg_score:.1f}%")
    c3.metric("Personal best", f"{best_score:.1f}%")

    st.subheader("🚀 Quick start")
    a, b, c = st.columns(3)
    with a:
        st.info("**Practice**\n\nTest your understanding with subject-wise MCQs.")
    with b:
        st.info("**Plan**\n\nOrganise your study sessions for the week.")
    with c:
        st.info("**Track**\n\nReview your quiz results and progress.")

    st.subheader("📚 Choose a subject")
    cols = st.columns(len(SUBJECTS))
    for col, subject in zip(cols, SUBJECTS):
        with col:
            st.markdown(f"**{subject}**")
            st.caption(f"{len(QUESTION_BANK[subject])} practice questions")

    st.caption("Includes 25 practice questions per core subject, with difficulty levels and explanations. Check your school syllabus and textbook for complete preparation.")

elif page == "🧠 Take a Quiz":
    st.title("🧠 Subject Quiz")
    subject = st.selectbox("Choose your subject", SUBJECTS)
    difficulty = st.selectbox("Choose difficulty", ["All levels", "Easy", "Medium", "Hard"])
    if difficulty == "All levels":
        questions = QUESTION_BANK[subject]
    else:
        questions = [q for q in QUESTION_BANK[subject] if q.get("difficulty", "Medium") == difficulty]
    st.write(f"Answer the {len(questions)} questions below.")
    st.caption("Choose All levels for the full subject question bank.")

    with st.form("quiz_form"):
        answers = {}
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q['q']}**  ` {q.get('difficulty', 'Medium')} `")
            answers[str(i)] = st.radio(
                "Choose one answer",
                q["options"],
                key=f"{subject}_{i}",
                index=None,
                label_visibility="collapsed"
            )
        submitted = st.form_submit_button("Submit quiz", type="primary")

    if submitted:
        unanswered = [i for i, value in answers.items() if value is None]
        if unanswered:
            st.warning("Please answer every question before submitting.")
        else:
            correct = sum(answers[str(i)] == q["answer"] for i, q in enumerate(questions))
            percentage = correct / len(questions) * 100
            record = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "subject": subject,
                "score": correct,
                "total": len(questions),
                "percentage": round(percentage, 1)
            }
            st.session_state.progress.append(record)
            save_progress(st.session_state.progress)
            st.session_state.last_quiz = {
                "subject": subject, "answers": answers, "correct": correct,
                "percentage": percentage, "questions": questions,
                "difficulty": difficulty
            }

    if ("last_quiz" in st.session_state
            and st.session_state.last_quiz["subject"] == subject
            and st.session_state.last_quiz.get("difficulty", "All levels") == difficulty):
        result = st.session_state.last_quiz
        st.divider()
        st.subheader("Your result")
        st.metric("Score", f"{result['correct']} / {len(result['questions'])}", f"{result['percentage']:.0f}%")
        if result["percentage"] >= 80:
            st.success("Excellent work! Keep it up.")
        elif result["percentage"] >= 50:
            st.info("Good effort. Review the explanations and try again.")
        else:
            st.warning("Keep practising. Learning improves step by step.")
        for i, q in enumerate(result["questions"]):
            chosen = result["answers"][str(i)]
            if chosen == q["answer"]:
                st.success(f"Q{i+1}: Correct — {q['answer']}")
            else:
                st.error(f"Q{i+1}: Your answer: {chosen} | Correct answer: {q['answer']}")
            st.caption(q["why"])

elif page == "📅 Study Planner":
    st.title("📅 Weekly Study Planner")
    st.write("Create a simple plan for your upcoming study sessions.")
    with st.form("planner_form"):
        study_date = st.date_input("Study date", value=date.today())
        subject = st.selectbox("Subject", SUBJECTS)
        topic = st.text_input("Topic to study", placeholder="e.g. Electrostatics")
        duration = st.number_input("Duration (minutes)", min_value=10, max_value=300, value=45, step=5)
        priority = st.select_slider("Priority", options=["Low", "Medium", "High"], value="Medium")
        add = st.form_submit_button("Add study task", type="primary")
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if add:
        if topic.strip():
            st.session_state.tasks.append({
                "Date": str(study_date), "Subject": subject,
                "Topic": topic.strip(), "Duration (min)": duration,
                "Priority": priority, "Done": False
            })
            st.success("Study task added.")
        else:
            st.warning("Please enter a topic.")
    if st.session_state.tasks:
        st.subheader("Your tasks")
        for i, task in enumerate(st.session_state.tasks):
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**{task['Subject']} — {task['Topic']}**")
            cols[0].caption(f"{task['Date']} · {task['Duration (min)']} min · {task['Priority']} priority")
            done = cols[1].checkbox("Done", value=task["Done"], key=f"task_{i}")
            st.session_state.tasks[i]["Done"] = done
            if cols[2].button("Delete", key=f"delete_{i}"):
                st.session_state.tasks.pop(i)
                st.rerun()
        completed = sum(t["Done"] for t in st.session_state.tasks)
        st.progress(completed / len(st.session_state.tasks))
        st.caption(f"{completed} of {len(st.session_state.tasks)} tasks completed")
        task_df = pd.DataFrame(st.session_state.tasks)
        st.download_button("Download study plan (CSV)", task_df.to_csv(index=False), "study_plan.csv", "text/csv")
    else:
        st.info("No tasks yet. Add your first study task above.")

elif page == "📝 My Notes":
    st.title("📝 Notes Creator")
    st.write("Write revision notes and download them for later.")
    note_title = st.text_input("Note title", "My Class 12 Revision Notes")
    subject = st.selectbox("Subject", SUBJECTS, key="notes_subject")
    note_body = st.text_area("Write your notes here", height=280, placeholder="Write definitions, formulas, key concepts and examples...")
    st.download_button(
        "⬇️ Download notes as TXT",
        data=f"{note_title}\nSubject: {subject}\nDate: {date.today()}\n\n{note_body}",
        file_name="revision_notes.txt",
        mime="text/plain",
        disabled=not note_body.strip()
    )
    st.download_button(
        "⬇️ Download notes as Markdown",
        data=f"# {note_title}\n\n**Subject:** {subject}  \n**Date:** {date.today()}\n\n{note_body}",
        file_name="revision_notes.md",
        mime="text/markdown",
        disabled=not note_body.strip()
    )

elif page == "📈 Progress":
    st.title("📈 Your Learning Progress")
    records = st.session_state.progress
    if not records:
        st.info("Complete a quiz to see your progress here.")
    else:
        df = pd.DataFrame(records)
        avg = df["percentage"].mean()
        c1, c2, c3 = st.columns(3)
        c1.metric("Quizzes", len(df))
        c2.metric("Average score", f"{avg:.1f}%")
        c3.metric("Best score", f"{df['percentage'].max():.1f}%")

        fig = px.line(
            df.reset_index(), x="index", y="percentage", color="subject",
            markers=True, title="Quiz score history",
            labels={"index": "Quiz number", "percentage": "Score (%)", "subject": "Subject"}
        )
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        subject_avg = df.groupby("subject", as_index=False)["percentage"].mean()
        fig2 = px.bar(subject_avg, x="subject", y="percentage",
                      title="Average score by subject", text_auto=".1f",
                      labels={"subject": "Subject", "percentage": "Average score (%)"})
        fig2.update_yaxes(range=[0, 100])
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Quiz history")
        st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
        st.download_button("Download progress CSV", df.to_csv(index=False), "quiz_progress.csv", "text/csv")
        if st.button("Clear quiz history", type="secondary"):
            st.session_state.progress = []
            save_progress([])
            if "last_quiz" in st.session_state:
                del st.session_state.last_quiz
            st.rerun()

st.divider()
st.caption("AI Study Buddy · Class 12 Capstone Project · Built using Streamlit. This version uses sample questions and local session/data storage; it does not connect to an AI model.")
