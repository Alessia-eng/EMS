import streamlit as st
from pathlib import Path
import pandas as pd
DATA_DIR = Path(__file__).parent / "data"

category_scoring = pd.read_csv(
    DATA_DIR / "category_scoring.csv"
)

tool_scoring = pd.read_csv(
    DATA_DIR / "tool_scoring.csv"
)
# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Energy Model Explorer",
    page_icon="⚡",
    layout="wide"
)


# ---------------------------------------------------------
# ASSETS
# ---------------------------------------------------------

ASSET_DIR = Path(__file__).parent / "assets"

IMAGES = {
    "operation": ASSET_DIR / "power_system_operation.png",
    "planning": ASSET_DIR / "power_system_planning.png",
    "integrated": ASSET_DIR / "integrated_energy_system_planning.png",
    "combination": ASSET_DIR / "combination.png",
}


# ---------------------------------------------------------
# MODELLING CATEGORIES
# ---------------------------------------------------------

CATEGORIES = {
    "operation": {
        "name": "Power-system operation",
        "icon": "⚡",
        "description": (
            "Focuses on operating the electrical system, including "
            "dispatch, power flows, network behaviour and operational constraints."
        ),
        "tools": [
            "PSS®E",
            "PowerFactory",
            "ETAP",
            "pandapower",
            "PSR NCP / SDDP",
        ],
    },

    "planning": {
        "name": "Power-system planning",
        "icon": "🏗️",
        "description": (
            "Focuses on how the power system should develop over time, "
            "including generation, transmission, capacity expansion and markets."
        ),
        "tools": [
            "PLEXOS",
            "PSR OptGen / SDDP",
            "NEPLAN",
            "WASP",
            "PyPSA",
            "FLEXTOOL",
            "Balmorel",
            "ReMIX",
        ],
    },

    "integrated": {
        "name": "Integrated energy-system planning",
        "icon": "🔄",
        "description": (
            "Focuses on the wider energy system, including multiple "
            "energy carriers, sectors and long-term energy transitions."
        ),
        "tools": [
            "TIMES",
            "MESSAGE-MAED",
            "MESSAGEix",
            "OSeMOSYS",
            "LEAP",
        ],
    },
}


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def image_exists(category):
    """Return True if an image exists for the category."""
    return IMAGES[category].exists()


def qualitative_level(score, maximum_score):
    """Convert an internal score into a qualitative label."""

    if maximum_score <= 0:
        return "Possible match"

    relative = score / maximum_score

    if relative >= 0.78:
        return "Very strong match"
    elif relative >= 0.58:
        return "Strong match"
    elif relative >= 0.38:
        return "Possible match"
    elif relative >= 0.18:
        return "Limited match"
    else:
        return "Poor match"


def calculate_scores(
    scope=None,
    purpose=None,
    timescale=None,
    network=None,
    priorities=None,
):
    """
    Calculate internal scores.

    The numbers are deliberately NOT shown to the learner.
    They are only used to create the qualitative ranking.
    """

    scores = {
        "operation": 0,
        "planning": 0,
        "integrated": 0,
    }

    # -----------------------------------------------------
    # QUESTION 1 — SCOPE
    # -----------------------------------------------------

    

    scope_row = category_scoring[
    (category_scoring["question"] == "Q1") &
    (category_scoring["answer"] == scope)
    ]

    if not scope_row.empty:
        scores["operation"] += int(scope_row.iloc[0]["operation"])
        scores["planning"] += int(scope_row.iloc[0]["planning"])
        scores["integrated"] += int(scope_row.iloc[0]["integrated"])

    # -----------------------------------------------------
    # QUESTION 2 — PURPOSE
    # -----------------------------------------------------

    

    purpose_row = category_scoring[
    (category_scoring["question"] == "Q2") &
    (category_scoring["answer"] == purpose)
    ]

    if not purpose_row.empty:
        scores["operation"] += int(purpose_row.iloc[0]["operation"])
        scores["planning"] += int(purpose_row.iloc[0]["planning"])
        scores["integrated"] += int(purpose_row.iloc[0]["integrated"])

    # -----------------------------------------------------
    # QUESTION 3 — TIME SCALE
    # -----------------------------------------------------

   

    timescale_row = category_scoring[
    (category_scoring["question"] == "Q3") &
    (category_scoring["answer"] == timescale)
    ]

    if not timescale_row.empty:
        scores["operation"] += int(timescale_row.iloc[0]["operation"])
        scores["planning"] += int(timescale_row.iloc[0]["planning"])
        scores["integrated"] += int(timescale_row.iloc[0]["integrated"])
    # -----------------------------------------------------
    # QUESTION 4 — REPRESENTATION
    # -----------------------------------------------------

   

    network_row = category_scoring[
    (category_scoring["question"] == "Q4") &
    (category_scoring["answer"] == network)
    ]

    if not network_row.empty:
        scores["operation"] += int(network_row.iloc[0]["operation"])
        scores["planning"] += int(network_row.iloc[0]["planning"])
        scores["integrated"] += int(network_row.iloc[0]["integrated"])

    # -----------------------------------------------------
    # QUESTION 5 — PRIORITIES
    # -----------------------------------------------------

    priority_scores = {
        "Open source": {},
        "Python / programmatic": {},
        "Commercial / industry use": {},
        "Long-term planning": {
            "planning": 3,
            "integrated": 2,
        },
        "Operational modelling": {
            "operation": 3,
        },
        "Market modelling": {
            "planning": 3,
            "integrated": 1,
        },
        "Detailed network modelling": {
            "operation": 3,
        },
        "Multiple energy carriers": {
            "integrated": 3,
            "planning": 1,
        },
        "Easy to learn": {},
    }

    if priorities:
        for priority in priorities:
            if priority in priority_scores:
                for category, value in priority_scores[priority].items():
                    scores[category] += value

    return scores

def get_ranking(scores):
    """Return modelling categories from strongest to weakest match."""
    return [
        category
        for category, score in sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

def combination_status(scores):
    """Return the current status of a combined modelling approach."""

    ranking = get_ranking(scores)

    first = ranking[0]
    second = ranking[1]

    if scores[first] == 0:
        return "Not enough information yet"

    difference = scores[first] - scores[second]

    if difference <= 2:
        return "Recommended"
    elif difference <= 5:
        return "Worth considering"
    else:
        return "Not currently required"

    

def rank_tools(category, priorities):
    tools = CATEGORIES[category]["tools"]

    tool_scores = {tool: 0 for tool in tools}

     
    for priority in priorities:
        if priority in tool_scoring.columns:
            for tool in tool_scores:
                row = tool_scoring[
                    (tool_scoring["tool"] == tool) &
                    (tool_scoring["category"] == CATEGORIES[category]["name"])
                ]

                if not row.empty:
                    tool_scores[tool] += int(row.iloc[0][priority])

    return sorted(
        tool_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]


def combination_reason(scores):
    """Explain why combination may or may not be relevant."""

    ranking = get_ranking(scores)

    first = ranking[0]
    second = ranking[1]

    if scores[first] == 0:
        return (
            "Answer a few questions first. The tool will then assess "
            "whether a combination is useful."
        )

    difference = scores[first] - scores[second]

    if difference <= 2:
        return (
            f"Your answers point strongly toward both "
            f"{CATEGORIES[first]['name']} and "
            f"{CATEGORIES[second]['name']}."
        )

    if difference <= 5:
        return (
            f"{CATEGORIES[first]['name']} is currently the strongest match, "
            f"but {CATEGORIES[second]['name']} may also be relevant."
        )

    return (
        f"Your answers currently point mainly toward "
        f"{CATEGORIES[first]['name']}."
    )


def show_category(category, level, expanded=False):
    data = CATEGORIES[category]

    # Traffic-light indicator for the category match
    if level in ["Very strong match", "Strong match"]:
        traffic_light = "🟢"
    elif level == "Possible match":
        traffic_light = "🟡"
    else:
        traffic_light = "🔴"

    col1, col2 = st.columns([1, 5])

    with col1:
        if image_exists(category):
            st.image(str(IMAGES[category]), width=110)
        else:
            st.markdown(
                f"<div style='font-size:55px; text-align:center;'>"
                f"{data['icon']}</div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.subheader(f"{data['name']}")
        st.write(f"{traffic_light} **{level}**")
        st.write(data["description"])

        st.markdown("**Example tools**")
        st.write(" · ".join(data["tools"]))


def show_results(
    scope=None,
    purpose=None,
    timescale=None,
    network=None,
    priorities=None,
    stage=None,
):
    """Display the current qualitative modelling result."""

    scores = calculate_scores(
        scope=scope,
        purpose=purpose,
        timescale=timescale,
        network=network,
        priorities=priorities,
    )

    answered = sum(
        value is not None
        for value in [scope, purpose, timescale, network]
    )

    if priorities:
        answered += 1

    if answered == 0:
        return

    ranking = get_ranking(scores)

    maximum_score = max(scores.values())

    st.divider()

    if stage:
        st.header(stage)

    st.write(
        "This is a **provisional result**. "
        "It will change as you provide more information."
    )

    # -----------------------------------------------------
    # RANKED CATEGORIES
    # -----------------------------------------------------

    for category in ranking:

        level = qualitative_level(
            scores[category],
            maximum_score,
        )

        show_category(
            category,
            level,
        )

    # -----------------------------------------------------
    # COMBINATION
    # -----------------------------------------------------

    st.divider()

    combination = combination_status(scores)

    if image_exists("combination"):
        col1, col2 = st.columns([1, 5])

        with col1:
            st.image(
                str(IMAGES["combination"]),
                width=110,
            )

        with col2:
            st.subheader("Combination recommended")
            st.write(f"**{combination}**")
            st.write(combination_reason(scores))
    else:
        st.subheader("🧩 Combination recommended")
        st.write(f"**{combination}**")
        st.write(combination_reason(scores))

# -----------------------------------------------------
    # TOOL RECOMMENDATIONS — QUESTION 5
    # -----------------------------------------------------

    if priorities:
        best_category = ranking[0]
        ranked_tools = rank_tools(best_category, priorities)

        st.divider()
        st.subheader("🛠️ Tools matching your priorities")

        for position, (tool, score) in enumerate(ranked_tools, start=1):
            st.write(f"**{position}. {tool}**")
# ---------------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------------

st.title("⚡ Energy Model Explorer")

st.write(
    "Explore which energy-system modelling approaches may fit "
    "your problem best."
)

st.divider()


# ---------------------------------------------------------
# MODE SELECTION
# ---------------------------------------------------------

mode = st.radio(
    "What would you like to do?",
    [
        "🧭 Help me choose",
        "🎯 Test my understanding",
    ],
    horizontal=True,
)


# =========================================================
# HELP ME CHOOSE
# =========================================================

if mode == "🧭 Help me choose":

    st.header("Help me choose a modelling approach")

    st.write(
        "Answer the questions below. The modelling match will "
        "develop as you provide more information."
    )

    # -----------------------------------------------------
    # QUESTION 1
    # -----------------------------------------------------

    st.subheader("1. What is the main scope of your analysis?")

    scope = st.radio(
        "Choose one:",
        [
            "Energy system",
            "Power system",
            "Both / integrated",
            "I'm not sure",
        ],
        index=None,
        key="scope",
    )

    if scope is not None:

        show_results(
            scope=scope,
            stage="Initial indication",
        )

        st.info(
            "At this stage we only know the broad scope. "
            "The next questions will make the recommendation more specific."
        )

    # -----------------------------------------------------
    # QUESTION 2
    # -----------------------------------------------------

    st.subheader("2. What do you mainly want to do?")

    purpose = st.radio(
        "Choose the main purpose:",
        [
            "Long-term planning / capacity expansion",
            "Short-term operation / dispatch",
            "Electricity-market analysis",
            "Network / power-flow analysis",
            "Energy-transition / scenario analysis",
            "A combination",
        ],
        index=None,
        key="purpose",
    )

    if purpose is not None:

        show_results(
            scope=scope,
            purpose=purpose,
            stage="After Question 2 — what changed?",
        )

        st.info(
            "Your purpose can substantially change the modelling match. "
            "For example, long-term capacity expansion points in a different "
            "direction from detailed short-term operation."
        )

    # -----------------------------------------------------
    # QUESTION 3
    # -----------------------------------------------------

    st.subheader("3. What time scale matters most?")

    timescale = st.radio(
        "Choose one:",
        [
            "Seconds to hours",
            "Days to months",
            "Years to decades",
            "Multiple time scales",
        ],
        index=None,
        key="timescale",
    )

    if timescale is not None:

        show_results(
            scope=scope,
            purpose=purpose,
            timescale=timescale,
            stage="After Question 3",
        )

    # -----------------------------------------------------
    # QUESTION 4
    # -----------------------------------------------------

    st.subheader(
        "4. What level of representation do you need?"
    )

    network = st.radio(
        "Choose one:",
        [
            "None / mainly energy balances",
            "Regional or zonal constraints",
            "Transmission network",
            "Detailed representation of the electrical system",
            "Multiple energy networks / energy carriers",
            "I'm not sure",
        ],
        index=None,
        key="network",
    )

    if network is not None:

        show_results(
            scope=scope,
            purpose=purpose,
            timescale=timescale,
            network=network,
            stage="After Question 4",
        )

    # -----------------------------------------------------
    # QUESTION 5
    # -----------------------------------------------------

    st.subheader(
        "5. What matters most when choosing a tool?"
    )

    priorities = st.multiselect(
        "Choose up to 3:",
        [
            "Open source",
            "Python / programmatic",
            "Commercial / industry use",
            "Long-term planning",
            "Operational modelling",
            "Market modelling",
            "Detailed network modelling",
            "Multiple energy carriers",
            "Easy to learn",
        ],
        max_selections=3,
        key="priorities",
    )

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    
    if priorities:

        scores = calculate_scores(
            scope=scope,
            purpose=purpose,
            timescale=timescale,
            network=network,
            priorities=[],
        )

        ranking = get_ranking(scores)
        best_category = ranking[0]

        

        ranked_tools = rank_tools(
            best_category,
            priorities,
        )
    
        st.divider()
        st.subheader("🛠️ Recommended modelling tools")

        st.write(
            f"Based on your modelling needs and your Question 5 preferences, "
            f"these are the strongest tool matches within "
            f"**{CATEGORIES[best_category]['name']}**:"
        )

        for position, (tool, score) in enumerate(
            ranked_tools,
            start=1,
        ):
            st.write(f"**{position}. {tool}**")

        st.success(
            "Your tool ranking is based on the preferences you selected "
            "in Question 5."
        )


# =========================================================
# TEST MY UNDERSTANDING
# =========================================================

else:

    
    # -----------------------------------------------------
# TEST MY UNDERSTANDING
# -----------------------------------------------------

    st.divider()
    st.header("🧠 Test my understanding")

    st.write(
        "Test your understanding of the main modelling concepts "
        "covered in this tool."
    )

    # Store whether each question has been checked
    for i in range(1, 6):
        if f"understanding_q{i}_checked" not in st.session_state:
            st.session_state[f"understanding_q{i}_checked"] = False


    # -----------------------------------------------------
    # QUESTION 1
    # -----------------------------------------------------

    question_1 = st.radio(
        "1. Which modelling category is mainly focused on short-term "
        "operation and dispatch of a power system?",
        [
            "Power-system operation",
            "Power-system planning",
            "Integrated energy-system planning",
        ],
        key="understanding_q1",
    )

    if st.button("Check answer 1"):
        st.session_state.understanding_q1_checked = True

    if st.session_state.understanding_q1_checked:
        if question_1 == "Power-system operation":
            st.success(
                "Correct! Power-system operation focuses on how the system "
                "operates over short time scales, including generation "
                "dispatch and other operational decisions."
            )
        else:
            st.error(
                "Not quite. The correct answer is Power-system operation."
            )


    # -----------------------------------------------------
    # QUESTION 2
    # -----------------------------------------------------

    question_2 = st.radio(
        "2. Which modelling category is most appropriate when the main objective "
        "is to decide what generation or network capacity should be built over "
        "the coming years or decades?",
        [
            "Power-system operation",
            "Power-system planning",
            "Integrated energy-system planning",
        ],
        key="understanding_q2",
    )

    if st.button("Check answer 2"):
        st.session_state.understanding_q2_checked = True

    if st.session_state.understanding_q2_checked:
        if question_2 == "Power-system planning":
            st.success(
                "Correct! Power-system planning focuses on longer-term decisions "
                "about generation, transmission, and system development."
            )
        else:
            st.error(
                "Not quite. The correct answer is Power-system planning."
            )


    # -----------------------------------------------------
    # QUESTION 3
    # -----------------------------------------------------

    question_3 = st.radio(
        "3. You want to study how electricity, heat, hydrogen and other energy "
        "carriers could develop together over several decades. Which category "
        "is the strongest match?",
        [
            "Power-system operation",
            "Power-system planning",
            "Integrated energy-system planning",
        ],
        key="understanding_q3",
    )

    if st.button("Check answer 3"):
        st.session_state.understanding_q3_checked = True

    if st.session_state.understanding_q3_checked:
        if question_3 == "Integrated energy-system planning":
            st.success(
                "Correct! Integrated energy-system planning considers multiple "
                "energy carriers and how different parts of the energy system "
                "interact over the long term."
            )
        else:
            st.error(
                "Not quite. The correct answer is "
                "Integrated energy-system planning."
            )


    # -----------------------------------------------------
    # QUESTION 4
    # -----------------------------------------------------

    question_4 = st.radio(
        "4. Why does the required level of network representation matter "
        "when choosing a modelling tool?",
        [
            "It determines whether the model needs to represent the electrical "
            "network in sufficient detail.",
            "It determines whether the model can only be used for short-term studies.",
            "It determines whether the model must be open source.",
        ],
        key="understanding_q4",
    )

    if st.button("Check answer 4"):
        st.session_state.understanding_q4_checked = True

    if st.session_state.understanding_q4_checked:
        if question_4 == (
            "It determines whether the model needs to represent the electrical "
            "network in sufficient detail."
        ):
            st.success(
                "Correct! Different modelling questions require different levels "
                "of representation, from mainly energy balances to regional "
                "constraints, transmission networks, or a detailed "
                "representation of the electrical system."
            )
        else:
            st.error(
                "Not quite. The level of network representation determines "
                "how much detail is needed in the electrical system."
            )


    # -----------------------------------------------------
    # QUESTION 5
    # -----------------------------------------------------

    question_5 = st.radio(
        "5. A study combines long-term capacity planning with multiple energy "
        "carriers and interactions between electricity, heat and hydrogen. "
        "Which approach is most likely to be appropriate?",
        [
            "Power-system operation only",
            "Power-system planning only",
            "Integrated energy-system planning, potentially combined "
            "with a power-system model",
        ],
        key="understanding_q5",
    )

    if st.button("Check answer 5"):
        st.session_state.understanding_q5_checked = True

    if st.session_state.understanding_q5_checked:
        if question_5 == (
            "Integrated energy-system planning, potentially combined "
            "with a power-system model"
        ):
            st.success(
                "Correct! The combination of long-term planning and multiple "
                "energy carriers points strongly toward integrated energy-system "
                "planning. A power-system model may also be useful when detailed "
                "electrical-system representation is required."
            )
        else:
            st.error(
                "Not quite. The correct answer is integrated energy-system "
                "planning, potentially combined with a power-system model."
            )
# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Energy Model Explorer — training prototype"
)