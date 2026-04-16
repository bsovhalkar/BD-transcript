#!/usr/bin/env python3
"""
Comprehensive Study Material Generator for BD: From Start to Scale
Processes all PDFs in mcq/ folder and generates structured study materials.
"""

import fitz  # PyMuPDF
import re
import os
import glob
from collections import defaultdict

MCQ_DIR = "mcq"
OUT_DIR = "Processed_Study_Material"

WEEK_TOPICS = {
    1: "Business Fundamentals",
    2: "Successful Businesses",
    3: "Industry and Business",
    4: "Industry, Market and Business",
    5: "Customer Characteristics",
    6: "Market and Market Descriptors",
    7: "Branding",
    8: "A New IT Start-up (Happiest Minds)",
    9: "Subsidiaries and Corporate Structure",
    10: "Value Chain Competencies",
    11: "Growth Strategies",
    12: "Pharma Transformation (Orchid Chemicals)",
}


def extract_pdf_text(path):
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)


def extract_notes_pdf(week):
    return extract_pdf_text(os.path.join(MCQ_DIR, f"notes w{week}.pdf"))


def read_lecture_notes(week):
    files = glob.glob(f"Notes/week_{week}_lec*.md")
    if files:
        with open(files[0]) as f:
            return f.read()
    return ""


def parse_mock_exam(filepath):
    """Parse a mock exam PDF into question dicts with answer keys."""
    doc = fitz.open(filepath)
    pages_text = [page.get_text() for page in doc]
    full_text = "\n".join(pages_text[:-1])
    answer_text = pages_text[-1] if pages_text else ""

    answers = {}
    for m in re.finditer(r"(\d+):\s*([A-D])", answer_text):
        answers[int(m.group(1))] = m.group(2)

    questions = []
    parts = re.split(r"\nQ(\d+)\. ", "\n" + full_text)
    for i in range(1, len(parts), 2):
        qnum = int(parts[i])
        body = parts[i + 1].strip()

        src_match = re.search(r"Source: (\S+)\s*\|\s*Difficulty: (\w+)", body)
        source = src_match.group(1) if src_match else ""
        difficulty = src_match.group(2) if src_match else ""

        week_match = re.search(r"_W(\d+)L", source)
        week = int(week_match.group(1)) if week_match else 0

        pre_source = body[: src_match.start()].strip() if src_match else body
        opt_match = re.search(r"\nA\)", pre_source)
        if opt_match:
            q_text = pre_source[: opt_match.start()].strip()
            opts_text = pre_source[opt_match.start():]
        else:
            q_text = pre_source
            opts_text = ""

        opts = {}
        for j, letter in enumerate(["A", "B", "C", "D"]):
            next_letter = ["B", "C", "D", None][j]
            if next_letter:
                m = re.search(rf"{letter}\)(.*?){next_letter}\)", opts_text, re.DOTALL)
            else:
                m = re.search(r"D\)(.*?)$", opts_text, re.DOTALL)
            if m:
                opts[letter] = m.group(1).strip()

        topic = re.sub(r"_", " ", re.sub(r"Lecture_W\d+L\d+_", "", source))
        mock_num = int(re.search(r"mock_exam_(\d+)", filepath).group(1))

        questions.append({
            "num": qnum, "text": q_text, "options": opts,
            "source": source, "topic": topic, "difficulty": difficulty,
            "week": week, "answer": answers.get(qnum, "?"), "mock_num": mock_num,
        })
    return questions


def load_all_mock_questions():
    """Load 5 unique mock exams, deduplicated, grouped by lecture week."""
    by_week = defaultdict(list)
    seen = set()
    for i in range(1, 6):
        path = os.path.join(MCQ_DIR, f"mock_exam_{i}.pdf")
        for q in parse_mock_exam(path):
            key = q["text"][:80]
            if key not in seen:
                seen.add(key)
                by_week[q["week"]].append(q)
    return by_week


def parse_assignment(week):
    path = os.path.join(MCQ_DIR, f"W{week} solution.pdf")
    if not os.path.exists(path):
        return []
    text = extract_pdf_text(path)
    questions = []
    parts = re.split(r"Q(\d+)\)", text)
    for i in range(1, len(parts), 2):
        qnum = int(parts[i])
        body = parts[i + 1].strip()
        opt_match = re.search(r"\na\s*[\.]", body)
        if opt_match:
            q_text = body[: opt_match.start()].strip()
            opts_text = body[opt_match.start():]
        else:
            q_text = body
            opts_text = ""
        q_text = re.sub(r"\s*QB\s*", " ", q_text).strip()

        opts = {}
        for j, letter in enumerate(["a", "b", "c", "d"]):
            next_letter = ["b", "c", "d", None][j]
            if next_letter:
                m = re.search(rf"{letter}\s*[\.]\s*(.*?)\n{next_letter}\s*[\.]", opts_text, re.DOTALL)
            else:
                m = re.search(rf"d\s*[\.]\s*(.*?)$", opts_text, re.DOTALL)
            if m:
                opts[letter.upper()] = m.group(1).strip()

        questions.append({
            "num": qnum, "text": q_text, "options": opts,
            "week": week, "answer": None, "difficulty": "Medium",
            "source": f"Week {week} Assignment", "topic": WEEK_TOPICS.get(week, ""),
        })
    return questions


# ─── GENERATED MCQs FOR WEEKS WITHOUT MOCK COVERAGE ───────────────────────
GENERATED_MCQS = {
    4: [
        {"text": "An industry is best defined as:", "options": {"A": "A single company producing goods", "B": "A group of companies producing substitute products that serve the same market", "C": "A government regulatory body", "D": "A consortium of supply chain partners"}, "answer": "B", "difficulty": "Easy", "topic": "Industry Definition", "explanation": "An industry comprises all companies producing substitute products serving the same customer need."},
        {"text": "The Demand Cascade refers to:", "options": {"A": "Rising demand during festival seasons", "B": "The funnel from total potential market to actual sales via economic and preferential filters", "C": "Sudden drop in demand after a product recall", "D": "Cascading effect of price cuts on competitors"}, "answer": "B", "difficulty": "Hard", "topic": "Demand Analysis", "explanation": "Demand Cascade describes how total potential market is filtered through economic and preference factors down to actual sales."},
        {"text": "Market Potential is best described as:", "options": {"A": "Current actual sales in the market", "B": "The absolute maximum demand for a product if all barriers are removed", "C": "Total revenue generated by top 5 players", "D": "Projected revenue for next fiscal year"}, "answer": "B", "difficulty": "Medium", "topic": "Market Analysis", "explanation": "Market potential is the maximum achievable demand assuming all constraints are lifted."},
        {"text": "Structural barriers in business development are best described as:", "options": {"A": "Short-term pricing tactics", "B": "Temporary market leadership positions", "C": "Durable defensive capabilities that make a strategy difficult to replicate", "D": "Government regulations limiting competition"}, "answer": "C", "difficulty": "Medium", "topic": "Competitive Strategy", "explanation": "Structural barriers are long-term defensive capabilities built into strategy to prevent replication by competitors."},
        {"text": "Which of the following is a characteristic of an oligopolistic market structure?", "options": {"A": "Thousands of small sellers with no price influence", "B": "A few large firms dominating the market with significant pricing power", "C": "Single seller with complete market control", "D": "Perfectly equal market share among all players"}, "answer": "B", "difficulty": "Easy", "topic": "Market Structure", "explanation": "Oligopoly features a few dominant firms with interdependent pricing and significant market power."},
        {"text": "Bottom-up demand forecasting in an industry typically begins with:", "options": {"A": "Macro-economic GDP projections", "B": "Government import/export data", "C": "Building estimates from individual customer or segment level", "D": "Industry association reports"}, "answer": "C", "difficulty": "Medium", "topic": "Demand Forecasting", "explanation": "Bottom-up forecasting aggregates individual customer-level estimates to arrive at total market demand."},
        {"text": "Test marketing is most appropriately conducted at the stage of:", "options": {"A": "Initial design concept", "B": "Fully finished product", "C": "Basic prototype", "D": "Manufacturing concept"}, "answer": "B", "difficulty": "Easy", "topic": "Market Testing", "explanation": "Test marketing is conducted on a fully finished product before full-scale launch to validate market acceptance."},
        {"text": "Which analytical tool helps a company assess its internal strengths and weaknesses against external opportunities and threats?", "options": {"A": "Porter's Five Forces", "B": "PESTLE Analysis", "C": "SWOT Analysis", "D": "BCG Matrix"}, "answer": "C", "difficulty": "Easy", "topic": "Strategic Analysis", "explanation": "SWOT Analysis evaluates internal Strengths & Weaknesses and external Opportunities & Threats."},
        {"text": "In strategic marketing for the Indian chemical industry, the primary focus should be on:", "options": {"A": "Individual consumers and households", "B": "Business users and industrial buyers", "C": "Government procurement only", "D": "Export markets exclusively"}, "answer": "B", "difficulty": "Easy", "topic": "B2B Marketing", "explanation": "Chemical industry products are predominantly industrial/B2B, so strategic marketing must target business users and industries."},
        {"text": "Market adoption primarily means:", "options": {"A": "First sale to an early adopter", "B": "Increasing brand awareness through advertising", "C": "Converting aware customers into actual regular users", "D": "Distribution channel expansion"}, "answer": "C", "difficulty": "Medium", "topic": "Market Adoption", "explanation": "Market adoption is the process of converting product-aware customers into committed, regular users."},
        {"text": "A premium pricing strategy works best for companies that are:", "options": {"A": "Cost-competitive and high-volume", "B": "New market entrants with limited brand equity", "C": "Differentiated or innovative with unique value propositions", "D": "Operating in commodity markets"}, "answer": "C", "difficulty": "Easy", "topic": "Pricing Strategy", "explanation": "Premium pricing is sustainable only when a firm offers differentiation or innovation that customers value highly."},
        {"text": "Analogy as a demand forecasting tool is most useful when:", "options": {"A": "Historical data for the product is abundant", "B": "The product is completely new and comparable analogous products exist", "C": "Statistical regression models are available", "D": "Sales data from last 5 years is available"}, "answer": "B", "difficulty": "Medium", "topic": "Demand Forecasting", "explanation": "Analogy forecasting leverages data from comparable products in analogous markets when direct data is unavailable."},
    ],
    5: [
        {"text": "The primary distinction between a Customer and a Consumer is:", "options": {"A": "Customers pay more than consumers", "B": "A customer buys the product; a consumer uses the product", "C": "Customers are always businesses; consumers are individuals", "D": "Consumers generate revenue; customers do not"}, "answer": "B", "difficulty": "Easy", "topic": "Customer vs Consumer", "explanation": "Customer = buyer (purchase decision), Consumer = user (product experience)."},
        {"text": "Which of the following best characterizes a B2B purchase?", "options": {"A": "Impulse-driven and emotionally influenced", "B": "Price-elastic with high volume of buyers", "C": "Procedure-bound, multi-tiered, and based on objective parameters", "D": "Heavily influenced by branding and packaging"}, "answer": "C", "difficulty": "Medium", "topic": "B2B Buying Behavior", "explanation": "B2B purchases involve formal procedures, multi-stakeholder decisions, and objective evaluation criteria."},
        {"text": "In a Business Market, demand for industrial products is typically:", "options": {"A": "Highly price-elastic", "B": "Derived from the demand for finished consumer goods", "C": "Independent of consumer market trends", "D": "Purely seasonal and cyclical"}, "answer": "B", "difficulty": "Medium", "topic": "Derived Demand", "explanation": "Industrial demand is derived — demand for steel rises when demand for automobiles rises."},
        {"text": "The inverted pyramid model of a customer-centric organization places at the top:", "options": {"A": "The CEO and top management", "B": "The Board of Directors", "C": "Frontline staff serving customers", "D": "Customers"}, "answer": "D", "difficulty": "Easy", "topic": "Customer-Centric Organization", "explanation": "In the modern inverted pyramid, customers sit at the top — the entire organization is oriented toward serving their needs."},
        {"text": "Which of the following defines the Buying Centre in organizational buying?", "options": {"A": "A physical procurement department", "B": "The CEO responsible for all purchases", "C": "All individuals and groups who participate in the purchasing decision", "D": "External consultants advising on purchases"}, "answer": "C", "difficulty": "Medium", "topic": "Organizational Buying", "explanation": "The buying centre includes all individuals involved in a B2B purchase decision."},
        {"text": "Consumer markets are characterized by:", "options": {"A": "Fewer buyers with rational, procedure-bound decisions", "B": "Millions of buyers with dynamic needs and emotional decision-making", "C": "Long-term supplier relationships with binding contracts", "D": "Inelastic demand driven by technical specifications"}, "answer": "B", "difficulty": "Easy", "topic": "Consumer Markets", "explanation": "Consumer markets have large numbers of individual buyers whose decisions are often emotional and influenced by branding."},
        {"text": "A homepreneur is best described as:", "options": {"A": "A real estate developer", "B": "An entrepreneur running a business from home", "C": "A large corporation with home delivery services", "D": "A franchise owner operating from residential property"}, "answer": "B", "difficulty": "Easy", "topic": "Entrepreneurship Types", "explanation": "A homepreneur is an entrepreneur who operates their business from their home."},
        {"text": "B2B Connect platforms primarily help companies in:", "options": {"A": "Direct advertising to end consumers", "B": "Building brand image in retail markets", "C": "Showcasing products and better utilization of capacities through industry networks", "D": "Reducing government compliance requirements"}, "answer": "C", "difficulty": "Medium", "topic": "B2B Platforms", "explanation": "B2B Connect platforms facilitate industry networking, product showcasing, and capacity utilization."},
        {"text": "In India, smartphones exemplify which type of market adoption pattern?", "options": {"A": "Slow, reluctant adoption", "B": "Price-driven, cautious adoption", "C": "Early and rapid adoption driven by aspirational demand", "D": "Late adoption after global markets matured"}, "answer": "C", "difficulty": "Easy", "topic": "Market Adoption", "explanation": "Smartphones in India saw early and rapid adoption driven by aspirational demand and digital connectivity."},
        {"text": "Which of the following is NOT a stage in the organizational buying process?", "options": {"A": "Problem Recognition", "B": "Supplier Search", "C": "Impulse Purchase", "D": "Post-Purchase Evaluation"}, "answer": "C", "difficulty": "Easy", "topic": "Buying Process", "explanation": "Organizational buying is systematic and deliberate. Impulse purchase is a consumer behavior concept."},
        {"text": "For a long-term future market growth indicator in India, a company might use:", "options": {"A": "Last quarter sales figures", "B": "Per capita consumption in India compared to the developed world", "C": "Current year advertising budget", "D": "Number of retail outlets"}, "answer": "B", "difficulty": "Medium", "topic": "Market Growth Analysis", "explanation": "India's per capita consumption vs developed nations reveals the headroom for long-term growth."},
        {"text": "B2B demand is typically described as inelastic because:", "options": {"A": "Industrial buyers negotiate hard on price", "B": "Once a product is proven and qualified, price becomes secondary to reliability", "C": "Governments regulate industrial pricing", "D": "There are few suppliers to choose from"}, "answer": "B", "difficulty": "Medium", "topic": "B2B Demand Characteristics", "explanation": "B2B demand inelasticity: once qualified, buyers keep using the product regardless of minor price changes."},
    ],
    6: [
        {"text": "Market segmentation divides a market into distinct groups based on:", "options": {"A": "Only demographic factors", "B": "Only geographic location", "C": "Shared characteristics, needs, or behaviors that require tailored strategies", "D": "Company revenue size"}, "answer": "C", "difficulty": "Easy", "topic": "Market Segmentation", "explanation": "Segmentation groups customers by shared characteristics to enable targeted strategies."},
        {"text": "Which type of market segmentation is based on lifestyle, values, and personality?", "options": {"A": "Demographic segmentation", "B": "Geographic segmentation", "C": "Psychographic segmentation", "D": "Behavioral segmentation"}, "answer": "C", "difficulty": "Easy", "topic": "Segmentation Types", "explanation": "Psychographic segmentation classifies customers by lifestyle, values, interests, and personality traits."},
        {"text": "The primary purpose of market positioning is to:", "options": {"A": "Set the price of the product", "B": "Establish the brand's distribution network", "C": "Create a distinct, valued image of the product in the target customer's mind", "D": "Determine production volumes"}, "answer": "C", "difficulty": "Easy", "topic": "Market Positioning", "explanation": "Positioning creates a clear, differentiated image in the customer's mind relative to competitive alternatives."},
        {"text": "A niche market strategy targets:", "options": {"A": "The entire mass market", "B": "A narrow, specific segment with specialized needs", "C": "International export markets only", "D": "All demographic age groups"}, "answer": "B", "difficulty": "Easy", "topic": "Niche Marketing", "explanation": "Niche strategy focuses on a small, well-defined segment where the company can become the dominant player."},
        {"text": "Which of the following best represents behavioral segmentation?", "options": {"A": "Targeting customers aged 25-35", "B": "Targeting customers in metro cities", "C": "Targeting heavy users who purchase weekly", "D": "Targeting customers who value luxury"}, "answer": "C", "difficulty": "Easy", "topic": "Behavioral Segmentation", "explanation": "Behavioral segmentation groups customers by usage patterns, purchase frequency, and loyalty."},
        {"text": "The correct sequence for strategic marketing (STP framework) is:", "options": {"A": "Segment, Target, Position, Execute", "B": "Position, Segment, Target, Execute", "C": "Target, Segment, Execute, Position", "D": "Execute, Target, Position, Segment"}, "answer": "A", "difficulty": "Easy", "topic": "STP Framework", "explanation": "The STP framework: Segment the market, Target the right segments, Position the product — then Execute."},
        {"text": "Market share is best measured as:", "options": {"A": "Total industry production volume", "B": "Company's sales as a percentage of total industry sales", "C": "Number of SKUs in the market", "D": "Number of distribution outlets"}, "answer": "B", "difficulty": "Easy", "topic": "Market Metrics", "explanation": "Market share = Company sales / Total market sales x 100. It measures competitive standing."},
        {"text": "The primary metric for assessing long-term market growth potential in India:", "options": {"A": "Current year stock market index", "B": "Population of metro cities only", "C": "Per capita consumption vs developed world benchmarks", "D": "Quarterly GDP growth rate"}, "answer": "C", "difficulty": "Medium", "topic": "Market Growth Indicators", "explanation": "Comparing India's per capita consumption with developed nations reveals the growth runway."},
        {"text": "Consumer loyalty programs are primarily designed to:", "options": {"A": "Reduce production costs", "B": "Build repeat purchase behavior and emotional brand attachment", "C": "Attract new first-time buyers only", "D": "Reduce advertising spend"}, "answer": "B", "difficulty": "Easy", "topic": "Customer Loyalty", "explanation": "Loyalty programs incentivize repeat purchases and build emotional connection, converting buyers into brand advocates."},
        {"text": "A market descriptor is primarily used to:", "options": {"A": "Set pricing benchmarks", "B": "Define the characteristics of a target market segment precisely", "C": "Track competitor sales data", "D": "Calculate market share"}, "answer": "B", "difficulty": "Medium", "topic": "Market Descriptors", "explanation": "Market descriptors precisely define segment characteristics, enabling companies to understand and target customers effectively."},
        {"text": "Which of the following is an example of geographic segmentation?", "options": {"A": "Targeting customers who buy premium products", "B": "Targeting millennials aged 22-35", "C": "Targeting urban consumers in Tier 1 cities separately from rural buyers", "D": "Targeting customers based on brand loyalty"}, "answer": "C", "difficulty": "Easy", "topic": "Geographic Segmentation", "explanation": "Geographic segmentation divides the market by location — region, city size, climate."},
        {"text": "Brand positioning that clearly differentiates from competitors is called the:", "options": {"A": "Point of Parity (POP)", "B": "Point of Difference (POD)", "C": "Point of Sale (POS)", "D": "Point of Contact (POC)"}, "answer": "B", "difficulty": "Medium", "topic": "Positioning Strategy", "explanation": "Point of Difference (POD) is the attribute that distinctly sets a brand apart from competitors."},
    ],
    7: [
        {"text": "A brand is most accurately defined as:", "options": {"A": "A company's logo and color scheme", "B": "The total experience, perception, and promise that a company represents in customers' minds", "C": "The registered trademark of a product", "D": "The product quality certification"}, "answer": "B", "difficulty": "Easy", "topic": "Brand Definition", "explanation": "A brand is far more than a logo — it is the complete set of perceptions, emotions, and expectations held by customers."},
        {"text": "Brand equity is best described as:", "options": {"A": "The book value of brand-related assets on the balance sheet", "B": "The premium value a brand adds over and above a generic equivalent", "C": "Total advertising spend on a brand", "D": "The number of brand extensions launched"}, "answer": "B", "difficulty": "Medium", "topic": "Brand Equity", "explanation": "Brand equity is the incremental value a brand name adds to a product versus an unbranded equivalent."},
        {"text": "In the Indian pharmaceutical industry, which factor primarily builds brand preference among doctors?", "options": {"A": "Price discounts to patients", "B": "Television advertising campaigns", "C": "Medical representative detailing and clinical evidence", "D": "Social media influencer marketing"}, "answer": "C", "difficulty": "Medium", "topic": "Pharma Branding", "explanation": "In pharma, medical representatives build brand preference through clinical evidence and personal doctor relationships."},
        {"text": "A brand extension strategy involves:", "options": {"A": "Launching a completely new brand for a new product category", "B": "Using an established brand name to enter a new product category", "C": "Reducing the brand portfolio to focus on one core brand", "D": "Rebranding after a company merger"}, "answer": "B", "difficulty": "Easy", "topic": "Brand Extension", "explanation": "Brand extension leverages existing brand equity by applying the trusted name to a new product category."},
        {"text": "A house of brands strategy refers to:", "options": {"A": "One master brand for all product lines", "B": "Multiple independent brands each with distinct identities under one parent company", "C": "Joint branding with competitor companies", "D": "Licensing brand names to franchisees"}, "answer": "B", "difficulty": "Medium", "topic": "Brand Architecture", "explanation": "House of brands (e.g., P&G) maintains separate brand identities (Tide, Pampers, Gillette) under one parent."},
        {"text": "Edible oil brands like Saffola distinguish themselves through:", "options": {"A": "Lowest price in the category", "B": "Heart-health positioning targeting health-conscious consumers", "C": "Industrial B2B supply agreements", "D": "Celebrity endorsement without a health message"}, "answer": "B", "difficulty": "Easy", "topic": "FMCG Brand Positioning", "explanation": "Saffola's heart-health positioning differentiates it in a commodity-like category by tapping into health-conscious values."},
        {"text": "The most powerful long-term brand asset a company can build is:", "options": {"A": "A large advertising budget", "B": "Customer loyalty that translates into advocacy and repeat purchases", "C": "The widest product range", "D": "Exclusive government contracts"}, "answer": "B", "difficulty": "Medium", "topic": "Brand Asset", "explanation": "Loyal customers who advocate for the brand provide sustainable competitive advantage."},
        {"text": "Evian water differentiates itself through:", "options": {"A": "Lowest price positioning", "B": "Premium Alpine purity heritage and lifestyle positioning", "C": "Widest distribution network", "D": "Highest volume production"}, "answer": "B", "difficulty": "Medium", "topic": "Brand Differentiation", "explanation": "Evian's brand is built on its Alpine source story and premium lifestyle association."},
        {"text": "Private label brands (store brands) compete primarily on:", "options": {"A": "Superior product innovation", "B": "Aspirational lifestyle positioning", "C": "Price advantage over national brands while maintaining acceptable quality", "D": "Exclusive technology patents"}, "answer": "C", "difficulty": "Easy", "topic": "Private Label Strategy", "explanation": "Private labels win on price — typically 20-40% cheaper than national brands."},
        {"text": "Brand awareness as the first step in brand equity means:", "options": {"A": "Customers remember exact product specifications", "B": "Customers can recognize or recall the brand when the category is mentioned", "C": "Customers have purchased the brand at least once", "D": "The brand has achieved >50% market share"}, "answer": "B", "difficulty": "Easy", "topic": "Brand Awareness", "explanation": "Brand awareness = recognition or recall. It is the necessary foundation for all other brand equity components."},
        {"text": "Which branding challenge is MOST specific to the pharmaceutical industry?", "options": {"A": "Need for consistent packaging design", "B": "Regulatory constraints on promotional claims and mandatory generic substitution", "C": "Managing retail shelf space", "D": "Running television advertisements"}, "answer": "B", "difficulty": "Hard", "topic": "Pharma vs FMCG Branding", "explanation": "Pharma faces unique regulatory challenges — claims must be clinically proven and generic substitution may undermine brand loyalty."},
        {"text": "Which of the following is an example of a branded house architecture?", "options": {"A": "P&G (Tide, Pampers, Ariel as separate brands)", "B": "Unilever (Dove, Lipton, Knorr as separate brands)", "C": "GE (all products carry the GE master brand)", "D": "Tata Group (multiple separate brand identities)"}, "answer": "C", "difficulty": "Medium", "topic": "Brand Architecture", "explanation": "Branded House = one master brand covers all products (GE Medical, GE Aviation, GE Capital all carry the GE brand)."},
    ],
    8: [
        {"text": "Happiest Minds Technologies differentiated itself from established IT players by:", "options": {"A": "Competing on cost and headcount arbitrage", "B": "Focusing on digital-native services (IoT, AI, Cloud) and a values-driven brand philosophy", "C": "Acquiring multiple legacy IT companies", "D": "Targeting only government sector contracts"}, "answer": "B", "difficulty": "Medium", "topic": "Happiest Minds Strategy", "explanation": "Happiest Minds positioned itself as a digital-native company with next-gen technologies rather than traditional IT outsourcing."},
        {"text": "A new IT start-up entering a mature, dominated market should primarily focus on:", "options": {"A": "Matching incumbents on price immediately", "B": "Identifying a differentiated niche and building a compelling value proposition", "C": "Replicating the largest player's business model", "D": "Targeting the same client segments as market leaders"}, "answer": "B", "difficulty": "Easy", "topic": "Startup Strategy", "explanation": "New entrants must find a differentiated niche — competing head-on with incumbents is a recipe for failure."},
        {"text": "Which of the following best describes a born digital company?", "options": {"A": "A traditional company that has launched a website", "B": "A company founded on digital technology as its core operating model from inception", "C": "A company that sells digital products online", "D": "A company that has undergone digital transformation"}, "answer": "B", "difficulty": "Easy", "topic": "Digital Business Models", "explanation": "Born digital companies are built from the ground up on digital architecture — their DNA is digital."},
        {"text": "The strategic significance of a successful IPO for a start-up includes:", "options": {"A": "Reducing the need for customer acquisition", "B": "Providing liquidity for founders, validating business model, and raising growth capital", "C": "Eliminating competition in the market", "D": "Securing government subsidies"}, "answer": "B", "difficulty": "Medium", "topic": "IPO Strategy", "explanation": "An IPO validates the company's business model publicly and provides capital for expansion."},
        {"text": "In IT services, high value per employee is achieved through:", "options": {"A": "Hiring the maximum number of employees", "B": "Focusing on commoditized, high-volume low-complexity work", "C": "Specializing in high-complexity, digital-native services that command premium pricing", "D": "Maximizing offshore headcount"}, "answer": "C", "difficulty": "Medium", "topic": "IT Business Model", "explanation": "High value-per-employee requires specialization in complex, emerging technology work where the market pays premium rates."},
        {"text": "A lighthouse customer strategy for a new IT start-up involves:", "options": {"A": "Targeting the smallest possible clients first", "B": "Winning one prestigious client whose reference validates the firm for other prospects", "C": "Building technology for the lighthouse industry sector", "D": "Acquiring existing clients from competitors"}, "answer": "B", "difficulty": "Hard", "topic": "Customer Acquisition Strategy", "explanation": "A lighthouse client provides the reference and credibility that opens doors to other clients."},
        {"text": "Technology foresight as a business development tool means:", "options": {"A": "Predicting exact technology releases from competitors", "B": "Identifying emerging technology trends early and building capabilities ahead of mainstream demand", "C": "Reverse-engineering competitor products", "D": "Tracking current technology adoption rates"}, "answer": "B", "difficulty": "Medium", "topic": "Technology Strategy", "explanation": "Technology foresight allows companies to position as experts in the next wave before it becomes mainstream."},
        {"text": "Organic growth in IT companies is primarily driven by:", "options": {"A": "Mergers and acquisitions of larger firms", "B": "Government contracts", "C": "Account expansion with existing clients and new client acquisition", "D": "Reducing headcount to improve margins"}, "answer": "C", "difficulty": "Easy", "topic": "Organic Growth", "explanation": "Organic growth in IT = expanding wallet share with existing clients + winning new clients."},
        {"text": "The primary challenge for a new IT company in its first three years is typically:", "options": {"A": "Excess demand from too many clients", "B": "Building credibility and track record without a reference-able client base", "C": "Managing too many employees", "D": "Over-investment in R&D"}, "answer": "B", "difficulty": "Medium", "topic": "Startup Challenges", "explanation": "The chicken-and-egg problem: clients want references, but references require clients."},
        {"text": "Digital transformation for an enterprise client means:", "options": {"A": "Moving the company's website to a new hosting provider", "B": "Fundamentally reimagining business processes and models using digital technologies to create new value", "C": "Hiring more IT staff", "D": "Purchasing the latest hardware infrastructure"}, "answer": "B", "difficulty": "Easy", "topic": "Digital Transformation", "explanation": "Digital transformation is about reimagining the business — new processes, new models, new value."},
        {"text": "Happiest Minds' happiness-focused brand philosophy was primarily a strategy to:", "options": {"A": "Reduce employee salaries", "B": "Attract and retain high-quality talent and build a distinctive culture-driven employer brand", "C": "Appeal to retail consumer markets", "D": "Compete on pricing with larger firms"}, "answer": "B", "difficulty": "Medium", "topic": "Employer Branding", "explanation": "In a talent war, a purpose-driven culture is a powerful differentiator for attracting top tech talent."},
        {"text": "Which is NOT a characteristic of a fragmented IT services market?", "options": {"A": "Many small players serving specialized niches", "B": "Low entry barriers for specialized services", "C": "One dominant player with over 70% market share", "D": "Clients distribute work across multiple vendors"}, "answer": "C", "difficulty": "Easy", "topic": "Market Structure", "explanation": "Fragmented markets have no single dominant player — many companies each hold small shares."},
    ],
    9: [
        {"text": "A wholly-owned subsidiary is best defined as:", "options": {"A": "A company where the parent holds exactly 50% of shares", "B": "A company 100% owned by a parent company, with full strategic control", "C": "A franchisee operating under a parent's brand", "D": "A joint venture with equal partner ownership"}, "answer": "B", "difficulty": "Easy", "topic": "Subsidiary Types", "explanation": "A wholly-owned subsidiary is 100% owned by the parent, giving full strategic and operational control."},
        {"text": "The primary strategic benefit of creating subsidiaries is:", "options": {"A": "Avoiding all tax obligations", "B": "Risk isolation, specialization, and enabling focused market entry without endangering the parent", "C": "Merging all operations into one legal entity", "D": "Reducing the need for corporate governance"}, "answer": "B", "difficulty": "Medium", "topic": "Subsidiary Strategy", "explanation": "Subsidiaries allow risk isolation and capital-efficient expansion."},
        {"text": "Tata Group's structure with multiple subsidiaries demonstrates:", "options": {"A": "A single-business focused strategy", "B": "A conglomerate strategy where diverse businesses operate under one parent umbrella", "C": "A merger and acquisition strategy within a single industry", "D": "An export-only growth strategy"}, "answer": "B", "difficulty": "Easy", "topic": "Conglomerate Structure", "explanation": "Tata Group is a classic conglomerate — diverse businesses across industries, each as separate subsidiaries."},
        {"text": "A Joint Venture (JV) differs from a wholly-owned subsidiary primarily in that:", "options": {"A": "A JV is always larger than a subsidiary", "B": "A JV is co-owned by two or more parties who share control and risk", "C": "A JV has no legal existence", "D": "A JV is only used for domestic operations"}, "answer": "B", "difficulty": "Easy", "topic": "Joint Ventures", "explanation": "JVs are partnerships where two or more entities share ownership, investment, risk, and decision-making."},
        {"text": "The key risk of an international Joint Venture is:", "options": {"A": "Generating too much profit too quickly", "B": "Conflicts arising from differing strategic priorities or profit-sharing disagreements between partners", "C": "Regulatory approval being too fast", "D": "Excessive market share"}, "answer": "B", "difficulty": "Medium", "topic": "JV Risks", "explanation": "JV conflicts arise from misaligned objectives, cultural clashes, or disputes over strategic direction."},
        {"text": "An Indian pharma company forming JVs with global players for oncology products gains primarily:", "options": {"A": "Lower production costs through volume", "B": "Access to proprietary technology, global regulatory expertise, and co-development capabilities", "C": "Complete ownership of the global partner's IP", "D": "Reduced competition from other Indian firms"}, "answer": "B", "difficulty": "Medium", "topic": "Strategic JVs", "explanation": "Pharma JVs for complex therapies give Indian companies access to technology, know-how, and global regulatory pathways."},
        {"text": "A step-down subsidiary refers to:", "options": {"A": "A subsidiary that is being wound down", "B": "A subsidiary of a subsidiary — a second-level indirect holding", "C": "A joint venture at the subsidiary level", "D": "A subsidiary with reduced equity interest"}, "answer": "B", "difficulty": "Hard", "topic": "Corporate Structure", "explanation": "Step-down subsidiaries are indirect holdings: Parent owns Sub A, which owns Sub B (step-down subsidiary of Parent)."},
        {"text": "Corporate restructuring through subsidiary carve-out IPOs allows a parent to:", "options": {"A": "Eliminate the subsidiary's operations", "B": "Unlock value by allowing market pricing of the subsidiary and raising fresh capital", "C": "Transfer all debt to the subsidiary", "D": "Reduce the subsidiary's workforce"}, "answer": "B", "difficulty": "Medium", "topic": "Corporate Finance Strategy", "explanation": "Carve-out IPOs allow the market to independently value a subsidiary, unlocking value obscured within a conglomerate."},
        {"text": "Which is a key reason why global companies use subsidiaries rather than direct branches for new markets?", "options": {"A": "Subsidiaries require less capital investment", "B": "Subsidiaries offer legal and financial separation, limiting parent liability", "C": "Subsidiaries don't require local regulatory approvals", "D": "Subsidiaries automatically receive tax exemptions"}, "answer": "B", "difficulty": "Medium", "topic": "Subsidiary Rationale", "explanation": "Legal separation through subsidiaries limits the parent's liability — subsidiary losses don't flow to the parent."},
        {"text": "An Indian auto JV that stuck to the JV product line and did not diversify is likely to:", "options": {"A": "Dominate the market in the long run", "B": "Fall behind as the market evolves beyond the limited JV product portfolio", "C": "Generate higher profits through specialization", "D": "Gain technology advantage over the global partner"}, "answer": "B", "difficulty": "Hard", "topic": "JV Limitations", "explanation": "Rigid adherence to a JV product line prevents adaptation — as markets evolve, the JV risks losing relevance."},
        {"text": "Hyundai's India operations demonstrate:", "options": {"A": "A licensing model without equity stake", "B": "A fully autonomous subsidiary with local manufacturing and tailored products for the Indian market", "C": "A joint venture with an Indian automaker", "D": "A pure export model from Korea"}, "answer": "B", "difficulty": "Medium", "topic": "Global Subsidiary Strategy", "explanation": "Hyundai India is a wholly-owned subsidiary with localized manufacturing and market-specific products."},
        {"text": "The concept of strategic autonomy in subsidiary management means:", "options": {"A": "The subsidiary operates independently without parent oversight", "B": "The subsidiary has freedom to adapt strategy within parent-defined boundaries to local market needs", "C": "The parent controls every operational decision", "D": "The subsidiary can acquire competitors without parent approval"}, "answer": "B", "difficulty": "Hard", "topic": "Subsidiary Management", "explanation": "Strategic autonomy balances local responsiveness with the parent's global strategy."},
    ],
}

# ─── STATIC CONTENT ────────────────────────────────────────────────────────
WEEK_MINDMAPS = {
    1: """## 🧠 Mind Map — Week 1\n\n```\nBusiness Development\n├── Sales (short-term, transactional)\n├── Marketing (market-centric, long-term)\n└── BD (partnerships, strategic value)\n\nStrategy Framework\n├── Vision → Mission → Objectives\n└── Plans & Projects\n\n8 States of Demand\n├── Negative, Latent, No Demand\n├── Declining, Irregular\n├── Full, Overfull\n└── Unwholesome\n```""",
    2: """## 🧠 Mind Map — Week 2\n\n```\nSustainable Growth Formula\n├── Product Innovation\n├── Operational Excellence\n└── Customer Fulfillment\n\nBD Overlay\n├── Strategic Marketing\n├── Brand Equity\n└── Customer Loyalty\n\nCase Studies\n├── Nirma (mass-market disruption)\n├── Honda (autonomous localization)\n└── Tesco (Consumer-First Paradigm)\n```""",
    3: """## 🧠 Mind Map — Week 3\n\n```\nIndustry Structure\n├── Business → Industry → Conglomerate\n├── Strategic Adjacency\n└── Porter's Five Forces\n\nKey Frameworks\n├── PESTLE\n├── SWOT\n└── Competitive Analysis\n```""",
    4: """## 🧠 Mind Map — Week 4\n\n```\nMarket Analysis\n├── Demand Cascade (funnel)\n├── Forecasting Methods\n│   ├── Statistical\n│   ├── Expert Opinion\n│   └── Analogy\n├── Market Adoption Curve\n└── Structural Barriers\n```""",
    5: """## 🧠 Mind Map — Week 5\n\n```\nCustomer Types\n├── Customer (buyer) vs Consumer (user)\n├── Consumer Market (B2C)\n│   ├── Emotional decisions\n│   └── Price-elastic demand\n└── Business Market (B2B)\n    ├── Derived demand\n    └── Buying Centre\n```""",
    6: """## 🧠 Mind Map — Week 6\n\n```\nSTP Framework\n├── Segment (DGPB types)\n├── Target (mass/niche/micro)\n└── Position (POD, POP)\n\nMarket Metrics\n├── Market Share\n├── Per Capita Consumption\n└── Loyalty Funnel\n```""",
    7: """## 🧠 Mind Map — Week 7\n\n```\nBrand Strategy\n├── Brand Equity\n│   ├── Awareness\n│   ├── Association\n│   ├── Perceived Quality\n│   └── Loyalty\n├── Architecture\n│   ├── House of Brands\n│   └── Branded House\n└── Applications\n    ├── Pharma (MR + evidence)\n    └── FMCG (Saffola, Evian)\n```""",
    8: """## 🧠 Mind Map — Week 8\n\n```\nIT Start-up Strategy\n├── Differentiation: Digital-native\n├── Niche positioning\n├── Lighthouse client strategy\n├── High value per employee\n└── Culture: Happiness brand\n```""",
    9: """## 🧠 Mind Map — Week 9\n\n```\nCorporate Structure\n├── Wholly-owned subsidiary (100%)\n├── JV (shared ownership)\n├── Step-down subsidiary\n└── Strategic benefits\n    ├── Risk isolation\n    ├── Market focus\n    └── Capital efficiency\n```""",
    10: """## 🧠 Mind Map — Week 10\n\n```\nValue Chain\n├── Primary: R&D, Mfg, Logistics, Sales, After-Sales\n├── Support: Finance, HR, IT, Legal\n├── Outsourcing (3rd party) vs Offshoring (another country)\n└── R&D Types: Basic → Applied → Developmental\n\nNegotiation\n└── Dual Concerns Model (Win-Win = High-High)\n```""",
    11: """## 🧠 Mind Map — Week 11\n\n```\nGrowth Strategies\n├── Industry Life Cycle: Intro → Growth → Maturity → Decline\n├── Competitive Turbulence: Maturity phase\n├── Endgame: Leadership, Niche, Harvesting, Divestment\n└── Stuck Industry: Fragmented + fails to evolve\n```""",
    12: """## 🧠 Mind Map — Week 12\n\n```\nPharma Transformation\n├── Orchid Chemicals: API focus\n├── Competitive Moat: Tech + Regulatory + Niche\n├── ANDA: US generic market entry\n└── Forward integration: API → Formulation → Export\n```""",
}

WEEK_SHORTCUTS = {
    1: """## ⚡ Shortcuts & Tricks — Week 1\n- **Sales vs BD**: Short-term (transaction) vs Long-term (partnerships)\n- **8 Demand States**: Negative, Latent, No Demand, Declining, Irregular, Full, Overfull, Unwholesome\n- **Strategy Roll-out**: → Plans & Projects (NOT goals/targets)\n- **Ford Model T**: Product **Standardisation** (not diversity)\n- **Inverted Pyramid**: Customers at the TOP""",
    2: """## ⚡ Shortcuts & Tricks — Week 2\n- **Growth Formula**: **POC** = Product Innovation + Operational Excellence + Customer Fulfillment\n- **Nirma**: Price + Promotion + Mass market (NOT alliances/innovation)\n- **SMART**: Specific Measurable Achievable Relevant Time-bound\n- **Strategic Adjacency**: Expand NEAR core (not unrelated)\n- **Honda**: Autonomous Localization = regional independence""",
    3: """## ⚡ Shortcuts & Tricks — Week 3\n- **Any company** can diversify (not just conglomerates)\n- **Porter's 5 Forces**: Rivalry + New Entrants + Substitutes + Buyer Power + Supplier Power\n- **PESTLE**: Political Economic Social Technological Legal Environmental\n- **SWOT**: Internal (S/W) + External (O/T)\n- **Industry evolution**: Business → Industry → Conglomerate""",
    4: """## ⚡ Shortcuts & Tricks — Week 4\n- **Demand Cascade**: Funnel from Total Potential → Actual Sales\n- **Disruption forecasting**: Expert Opinions + Simulations (NOT linear models)\n- **Analogy method**: New product + comparable existing product\n- **Test marketing**: FULLY FINISHED product only\n- **Premium pricing**: Only for DIFFERENTIATED firms""",
    5: """## ⚡ Shortcuts & Tricks — Week 5\n- **Customer = Pays | Consumer = Uses**\n- **B2B**: Multi-tier, rational, procedure-bound\n- **B2B demand**: DERIVED from consumer demand → INELASTIC once proven\n- **Inverted Pyramid**: Customers at top\n- **Homepreneur**: Home-based entrepreneur""",
    6: """## ⚡ Shortcuts & Tricks — Week 6\n- **STP order**: Segment → Target → Position (always this sequence)\n- **DGPB**: Demographic, Geographic, Psychographic, Behavioral\n- **India growth metric**: Per capita vs developed world\n- **Niche**: Small segment + specialized needs\n- **Loyalty funnel**: Awareness → Trial → Adoption → Loyalty → Advocacy""",
    7: """## ⚡ Shortcuts & Tricks — Week 7\n- **Brand = Promise** to customers\n- **Brand Equity**: Awareness → Association → Perceived Quality → Loyalty\n- **House of Brands** (P&G) vs **Branded House** (GE)\n- **Pharma**: MR + Clinical evidence (not mass advertising)\n- **Saffola**: Heart-health = differentiation in commodity market""",
    8: """## ⚡ Shortcuts & Tricks — Week 8\n- **New IT formula**: Differentiation + Niche = avoid confrontation with giants\n- **Happiest Minds**: Digital-native (IoT + AI + Cloud) + Values culture\n- **Lighthouse client**: One reference = many doors opened\n- **High value/employee**: Complex tech = premium rates\n- **Born digital**: Digital DNA from founding""",
    9: """## ⚡ Shortcuts & Tricks — Week 9\n- **Wholly-owned**: 100% ownership + full control\n- **JV**: Shared ownership + shared risk (conflict-prone)\n- **Step-down**: Parent → Sub A → Sub B (indirect)\n- **Tata**: Classic conglomerate with subsidiary structure\n- **Carve-out IPO**: Unlocks hidden subsidiary value""",
    10: """## ⚡ Shortcuts & Tricks — Week 10\n- **Out**sourcing = **Out**side party | **Off**shoring = **Off** to another country\n- **Basic Research**: Pure knowledge + VERY LONG timeline\n- **Win-Win negotiation**: HIGH concern for BOTH self and others\n- **Cultural Blinds**: Stereotyping + self-centrism mindsets\n- **Primary activities**: Those that directly touch the product""",
    11: """## ⚡ Shortcuts & Tricks — Week 11\n- **Competitive Turbulence**: MATURITY phase (not growth!)\n- **Follower strategy**: Fragmented market + cost leadership + LOW returns\n- **Stuck industry**: Fragmented + fails to evolve\n- **Endgame**: Leadership, Niche, Harvesting, Divestment (NOT Innovation)\n- **First-mover**: INTRODUCTION phase advantage""",
    12: """## ⚡ Shortcuts & Tricks — Week 12\n- **Orchid moat**: Technology + Regulatory (ANDA) + Niche\n- **ANDA**: Abbreviated New Drug Application (US generic entry)\n- **Forward integration**: API → Finished Dosage → Marketing\n- **Generic erosion**: Rapid price drop after multiple generics enter\n- **Pharma success**: Niche + tech + regulatory = sustainable advantage""",
}

WEEK_MEMORY_AIDS = {
    1: """## 📌 Memory Aids — Week 1\n\n| Concept | Mnemonic |\n|---------|----------|\n| 3 Functions | **SaMBa**: Sales + Marketing + Business Development |\n| Strategy Roll-out | Plans & Projects (not goals/targets) |\n| Ford Model T | "Any color as long as it's black" = **Standardisation** |\n| Inverted Pyramid | Customers **crown** the organization |\n| 8 Demand States | NLDIFOUU: Negative Latent Declining Irregular Full Overfull Unwholesome (+ No demand) |""",
    2: """## 📌 Memory Aids — Week 2\n\n| Concept | Mnemonic |\n|---------|----------|\n| Growth Formula | **POC** = Product + Operational + Customer |\n| SMART | Specific **M**easurable **A**chievable **R**elevant **T**ime-bound |\n| Nirma | **PAM**: Price + Advertising + Mass market |\n| Honda | **AL**: Autonomous Localization |\n| Strategic Adjacency | "Ripples from a stone — expand outward from core" |""",
    3: """## 📌 Memory Aids — Week 3\n\n| Concept | Mnemonic |\n|---------|----------|\n| Porter's 5 Forces | **SNBRS**: Supplier, New entrants, Buyer, Rivalry, Substitutes |\n| PESTLE | **P**olitical **E**conomic **S**ocial **T**echnological **L**egal **E**nvironmental |\n| Business evolution | Seed → Plant → Forest = Business → Multi-business → Industry |\n| Conglomerate rule | ANY company can diversify |""",
    4: """## 📌 Memory Aids — Week 4\n\n| Concept | Mnemonic |\n|---------|----------|\n| Demand Cascade | Water filtering through layers of a funnel |\n| Adoption curve | **IEELLL**: Innovators, Early Adopters, Early Majority, Late Majority, Laggards |\n| Analogy forecast | "Find a twin product in a similar market" |\n| Premium pricing | "Premium = Differentiation only" |""",
    5: """## 📌 Memory Aids — Week 5\n\n| Concept | Mnemonic |\n|---------|----------|\n| Customer vs Consumer | **Customer Chooses, Consumer Consumes** |\n| B2B Buying Centre | **UIDBG**: Users, Influencers, Deciders, Buyers, Gatekeepers |\n| B2B Demand | "Derived = downstream dependent" |\n| B2C vs B2B | B2C = Emotional/Brand; B2B = Rational/Relationship |""",
    6: """## 📌 Memory Aids — Week 6\n\n| Concept | Mnemonic |\n|---------|----------|\n| STP | "Slice → Take aim → Plant the flag" |\n| Segmentation | **DGPB** = Demographic, Geographic, Psychographic, Behavioral |\n| Loyalty funnel | **ATALA**: Awareness → Trial → Adoption → Loyalty → Advocacy |\n| Niche | "Small pond, big fish" |""",
    7: """## 📌 Memory Aids — Week 7\n\n| Concept | Mnemonic |\n|---------|----------|\n| Brand Equity | **AAPL**: Awareness + Association + Perceived quality + Loyalty |\n| Brand Architecture | P&G = House of Brands | GE = Branded House |\n| Pharma branding | **DRE**: Doctor + Rep + Evidence |\n| Saffola | Heart ❤️ = Health in oil category |""",
    8: """## 📌 Memory Aids — Week 8\n\n| Concept | Mnemonic |\n|---------|----------|\n| Happiest Minds | Happy + Smart + Digital = Culture + AI/IoT/Cloud |\n| Start-up entry | "Find a gap, own a niche, then expand" |\n| Lighthouse client | "One bright lighthouse guides many ships" |\n| Born digital | "Born with a smartphone, not migrated to one" |""",
    9: """## 📌 Memory Aids — Week 9\n\n| Concept | Mnemonic |\n|---------|----------|\n| Wholly-owned | "100% owned = 100% control = 100% risk isolated" |\n| JV risk | "Two captains = ship problems" |\n| Step-down | "Grandparent → Parent → Child" |\n| Tata Group | "Tree with many branches (subsidiaries)" |""",
    10: """## 📌 Memory Aids — Week 10\n\n| Concept | Mnemonic |\n|---------|----------|\n| Outsourcing vs Offshoring | "Out**source** = someone else; Off**shore** = somewhere else" |\n| R&D hierarchy | Basic → Applied → Developmental = Knowledge → Science → Product |\n| Win-Win | "High-High = Win-Win" |\n| Value chain | "Primary = makes product; Support = enables making" |""",
    11: """## 📌 Memory Aids — Week 11\n\n| Concept | Mnemonic |\n|---------|----------|\n| PLC stages | **IGMD**: Introduction, Growth, Maturity, Decline |\n| Competitive Turbulence | "Turbulence = too many players in Maturity" |\n| Stuck industry | "Stuck = can't move forward = no resources or wrong vision" |\n| Endgame | **LNHD**: Leadership, Niche, Harvesting, Divestment |""",
    12: """## 📌 Memory Aids — Week 12\n\n| Concept | Mnemonic |\n|---------|----------|\n| Orchid's transformation | API → Formulation → Export = molecule to market |\n| ANDA | "A New Drug Application for generic entry" |\n| Competitive moat | **TRN**: Technology + Regulation + Niche |\n| Pharma lesson | "Small beats big with niche + tech + regulatory" |""",
}

WEEK_FORMULA_SHEETS = {
    1: """## 📐 Formula & Framework Sheet — Week 1\n\n| Framework | Detail |\n|-----------|--------|\n| **Strategy Roll-out** | Vision → Mission → Objectives → Plans & Projects |\n| **BD Definition** | BD = Strategic Partnerships → Long-term Value |\n| **AMA Marketing** | Creating, Communicating, Delivering & Exchanging value |\n| **Sales Process** | Prospect → Qualify → Demo → Close → Repeat |""",
    2: """## 📐 Formula & Framework Sheet — Week 2\n\n| Framework | Detail |\n|-----------|--------|\n| **Growth Formula** | Product Innovation × Operational Excellence × Customer Fulfillment |\n| **SMART Goals** | Specific + Measurable + Achievable + Relevant + Time-bound |\n| **BD Overlay** | Strategic Marketing + Brand Equity + Customer Loyalty + Firm-Customer Connect |\n| **Demand Estimation** | Top-Down OR Bottom-Up (both valid) |""",
    3: """## 📐 Formula & Framework Sheet — Week 3\n\n| Framework | Detail |\n|-----------|--------|\n| **Porter's 5 Forces** | Rivalry + New Entrants + Substitutes + Buyer Power + Supplier Power |\n| **PESTLE** | Political + Economic + Social + Technological + Legal + Environmental |\n| **SWOT** | Strengths + Weaknesses + Opportunities + Threats |\n| **Competitive Advantage** | Differentiation OR Cost Leadership |""",
    4: """## 📐 Formula & Framework Sheet — Week 4\n\n| Framework | Detail |\n|-----------|--------|\n| **Demand Cascade** | Total Potential → Addressable → Served → Actual Sales |\n| **Market Share** | Company Sales / Total Industry Sales × 100% |\n| **Adoption Curve** | Innovators → Early Adopters → Early Majority → Late Majority → Laggards |\n| **Market Penetration** | Current Users / Total Potential Users × 100% |""",
    5: """## 📐 Formula & Framework Sheet — Week 5\n\n| Framework | Detail |\n|-----------|--------|\n| **Customer Lifetime Value** | Avg Purchase Value × Frequency × Customer Lifespan |\n| **Derived Demand** | Industrial Demand = f(Consumer Demand for final product) |\n| **B2B Value in Use** | Value = Revenue Generated OR Cost Saved |\n| **NPS** | % Promoters – % Detractors |""",
    6: """## 📐 Formula & Framework Sheet — Week 6\n\n| Framework | Detail |\n|-----------|--------|\n| **STP** | Segment → Target → Position |\n| **Market Growth Rate** | (Current – Previous) / Previous × 100% |\n| **TAM/SAM/SOM** | Total → Serviceable Available → Serviceable Obtainable Market |\n| **Per Capita** | Total Consumption / Population |""",
    7: """## 📐 Formula & Framework Sheet — Week 7\n\n| Framework | Detail |\n|-----------|--------|\n| **Brand Equity (Keller)** | Identity → Meaning → Response → Resonance |\n| **Price Premium** | Brand Price – Generic Price |\n| **NPS** | % Promoters (9-10) – % Detractors (0-6) |\n| **Brand Extension Rule** | Extend when: Brand Fit + Category Potential + Execution |""",
    8: """## 📐 Formula & Framework Sheet — Week 8\n\n| Framework | Detail |\n|-----------|--------|\n| **Revenue per Employee** | Total Revenue / Headcount |\n| **CAC** | Total Sales & Marketing Spend / New Customers |\n| **LTV:CAC** | Healthy ratio > 3:1 |\n| **Digital Maturity** | Technology + Talent + Culture + Strategy |""",
    9: """## 📐 Formula & Framework Sheet — Week 9\n\n| Framework | Detail |\n|-----------|--------|\n| **Ownership Levels** | Wholly-owned=100%; Majority=>50%; Minority=<50% |\n| **Effective Ownership** | Parent (80%) → Sub A (70%) → Effective = 56% |\n| **Subsidiary ROI** | Subsidiary PAT / Investment × 100% |\n| **JV Control** | Voting Power = % Equity Stake (unless special provisions) |""",
    10: """## 📐 Formula & Framework Sheet — Week 10\n\n| Framework | Detail |\n|-----------|--------|\n| **Value Chain Margin** | Value Added = Revenue – Cost of Inputs at each stage |\n| **Make vs Buy** | Make: Core + Strategic | Buy: Non-core + Cost efficient |\n| **BATNA** | Best Alternative to Negotiated Agreement |\n| **R&D Intensity** | R&D Spend / Revenue × 100% |""",
    11: """## 📐 Formula & Framework Sheet — Week 11\n\n| Framework | Detail |\n|-----------|--------|\n| **Market Share** | Company Revenue / Total Industry Revenue × 100% |\n| **CAGR** | (End / Start)^(1/n) – 1 |\n| **BCG Matrix** | Market Share vs Market Growth → Stars/Cash Cows/Dogs/Question Marks |\n| **Ansoff Matrix** | Market Penetration, Market Development, Product Development, Diversification |""",
    12: """## 📐 Formula & Framework Sheet — Week 12\n\n| Framework | Detail |\n|-----------|--------|\n| **Pharma Pipeline Value** | Σ (Market Size × Win Probability × Margin) |\n| **Gross Margin** | (Revenue – COGS) / Revenue × 100% |\n| **Generic Price Erosion** | First generic: ~80% branded price; 2+ generics: drops to ~20% |\n| **R&D-to-Revenue** | Global pharma R&D ≈ 15-20% of revenue |""",
}

WEEK_FREQUENTLY_ASKED = {
    1: ["Strategic marketing focus: **Market Segmentation**", "BD seeks: **Long-term partnerships**", "Negative demand: consumers **dislike and avoid**", "Ford Model T: **Product Standardisation**", "Strategy rolled out as: **Plans and Projects**", "Marketing effectiveness key component: **Advertising and Communication**", "Strategic marketing time: **Medium and long term (2-3 years)**", "Inverted pyramid top: **Customers**"],
    2: ["Growth Formula: **Product Innovation + Operational Excellence + Customer Fulfillment**", "SMART: **Specific, Measurable, Achievable, Relevant, Time-bound**", "Nirma: **affordable pricing + targeted promotion = mass-market**", "Honda: **Autonomous Localization**", "Strategic Adjacency: expand into **closely related** areas", "Demand estimation can be **both top-down and bottom-up**", "Test marketing: **Fully Finished Product**"],
    3: ["Any company can diversify — **not just conglomerates**", "Porter's Five Forces: 5 competitive forces", "PESTLE: 6 macro-environmental factors", "Strategic Adjacency: expand near core", "Industry = group of substitutes serving same market"],
    4: ["Demand Cascade: funnel from Total Potential to **Actual Sales**", "Disruption forecasting: **Expert opinions with simulations**", "Analogy: for **new products with analogous comparables**", "Test marketing: **Fully finished product**", "Premium pricing: **Differentiated firms only**", "Adoption: Innovators → Early Adopters → Early/Late Majority → Laggards"],
    5: ["Customer = **buys** | Consumer = **uses**", "B2B: **multi-tiered, procedure-bound, rational**", "B2B demand is **derived** from consumer product demand", "Inverted pyramid: **Customers at top**", "Homepreneur = **home-based entrepreneur**", "B2B demand: **inelastic** once product proven"],
    6: ["STP: **Segment → Target → Position**", "Psychographic: **lifestyle, values, personality**", "India growth: **per capita vs developed world**", "Niche: **narrow, specific segment**", "Loyalty funnel: Awareness → Trial → Adoption → Loyalty → Advocacy"],
    7: ["Brand = **total experience and promise** (not just a logo)", "Brand Equity: Awareness → Association → Perceived Quality → Loyalty", "Pharma: **MR + Clinical evidence**", "Brand Extension: apply name to **new product category**", "Saffola: **heart-health positioning**", "Evian: **Premium Alpine heritage**"],
    8: ["Happiest Minds: **digital-native** (IoT, AI, Cloud)", "New IT start-up: **differentiate + niche**", "Lighthouse client: one reference **opens multiple doors**", "High value/employee: **complex, specialized tech**", "Born digital = **digital DNA from founding**"],
    9: ["Wholly-owned: **100% parent ownership**", "JV: **shared ownership and control**", "Step-down: **subsidiary of a subsidiary**", "Tata = **conglomerate with subsidiaries**", "JV risk: **misaligned strategic priorities**", "Carve-out IPO: **unlocks subsidiary value**"],
    10: ["Outsourcing = **third party** | Offshoring = **another country**", "Basic Research: **pure knowledge, very long timeline**", "Win-Win: **High concern for BOTH self and others**", "Cultural Blinds: **mindsets blocking cross-cultural interaction**", "Primary activities include: R&D, Manufacturing, Logistics, Sales, After-Sales", "Apex Leadership: **Wisdom**"],
    11: ["Competitive Turbulence: **Maturity** phase", "Follower strategy: **market fragmentation, cost leadership, low returns**", "Stuck: **fragmented + fails to evolve**", "Endgame: Leadership, Niche, Harvesting, Divestment (**NOT Innovation**)", "First-mover: **Introduction** phase"],
    12: ["Orchid moat: **Technology + Regulatory + Niche**", "ANDA: **Abbreviated New Drug Application**", "Forward integration: **API → Formulation → Marketing**", "Generic erosion: **rapid after multiple generics**", "Pharma success: **niche + tech + regulatory**"],
}


# ─── NOTES GENERATOR ───────────────────────────────────────────────────────
def generate_notes_md(week, notes_text, lecture_notes_text):
    topic = WEEK_TOPICS[week]
    
    # Clean notes text
    lines_raw = [l.strip() for l in notes_text.split("\n") if l.strip() and len(l.strip()) > 2]
    
    # Split into sections
    concept_lines = []
    detail_lines = []
    found_core = False
    found_detail = False
    for ln in lines_raw:
        if any(kw in ln for kw in ["Core Concepts", "Core concepts"]):
            found_core = True
            continue
        if any(kw in ln for kw in ["Detailed Analysis", "Key Steps", "Introduction"]) and found_core:
            found_detail = True
        if found_core and not found_detail:
            concept_lines.append(ln)
        elif found_detail:
            detail_lines.append(ln)

    # Opening paragraph
    intro_lines = []
    for ln in lines_raw[:8]:
        if any(kw in ln for kw in ["Core Concepts", "Term", "Definition", "Introduction"]):
            break
        intro_lines.append(ln)

    out = []
    out.append(f"# Week {week} — {topic}")
    out.append(f"> **Course:** Business Development: From Start to Scale | **Week:** {week} of 12")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 📋 Table of Contents")
    out.append("1. [Core Concepts](#core-concepts)")
    out.append("2. [Detailed Analysis](#detailed-analysis)")
    out.append("3. [Key Takeaways & Frequently Asked Points](#key-takeaways)")
    out.append("4. [Mind Map](#mind-map)")
    out.append("5. [Shortcuts & Tricks](#shortcuts--tricks)")
    out.append("6. [Memory Aids](#memory-aids)")
    out.append("7. [Formula & Framework Sheet](#formula--framework-sheet)")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## �� Core Concepts")
    out.append("")
    if intro_lines:
        out.append(" ".join(intro_lines))
        out.append("")

    # Key definitions from lecture notes
    if lecture_notes_text:
        import re
        # Find tables and key definitions
        tables = re.findall(r"\| [A-Z][^\n]+ \|[^\n]+\|[^\n]+\|(?:\n\|[^\n]+\|)+", lecture_notes_text)
        if tables:
            out.append("### Key Definitions from Lecture Notes")
            out.append("")
            out.append(tables[0][:1200] if len(tables[0]) > 1200 else tables[0])
            out.append("")

    # Concept lines as bullet points
    if concept_lines:
        out.append("### Core Concepts Overview")
        out.append("")
        for ln in concept_lines[:25]:
            if ln not in ["Term", "Definition", "Significance"] and len(ln) > 5:
                out.append(f"- {ln}")
        out.append("")

    out.append("---")
    out.append("")
    out.append("## 🔍 Detailed Analysis")
    out.append("")

    # Lecture notes key sections
    if lecture_notes_text:
        import re
        sections = re.split(r"\n### ", lecture_notes_text)
        count = 0
        for sec in sections[1:]:
            if count >= 4:
                break
            lines_sec = sec.split("\n")
            title = lines_sec[0].strip()
            if any(skip in title for skip in ["Table of Contents", "About the", "Key Topics"]):
                continue
            body = "\n".join(lines_sec[1:])
            # Strip complex tables, keep prose
            body = re.sub(r"\|[^\n]+\|[^\n]+\n", "", body)
            body = body[:500].strip()
            if len(body) > 50:
                out.append(f"### {title}")
                out.append("")
                out.append(body)
                out.append("")
                count += 1

    # Detail from notes PDF
    if detail_lines:
        out.append("### From Course Notes PDF")
        out.append("")
        para = []
        for ln in detail_lines[:35]:
            if ln.startswith(("•", "◦", "▪")):
                if para:
                    out.append(" ".join(para))
                    para = []
                out.append(f"- {ln.lstrip(chr(8226)+chr(9702)+chr(9642)+chr(32))}")
            else:
                para.append(ln)
        if para:
            out.append(" ".join(para))
        out.append("")

    out.append("---")
    out.append("")
    out.append("## ✅ Key Takeaways & Frequently Asked Points")
    out.append("")
    out.append("*These concepts and facts appear most frequently in assignments and mock exams:*")
    out.append("")
    for i, point in enumerate(WEEK_FREQUENTLY_ASKED.get(week, []), 1):
        out.append(f"{i}. {point}")
    out.append("")
    out.append("---")
    out.append("")
    out.append(WEEK_MINDMAPS.get(week, ""))
    out.append("")
    out.append("---")
    out.append("")
    out.append(WEEK_SHORTCUTS.get(week, ""))
    out.append("")
    out.append("---")
    out.append("")
    out.append(WEEK_MEMORY_AIDS.get(week, ""))
    out.append("")
    out.append("---")
    out.append("")
    out.append(WEEK_FORMULA_SHEETS.get(week, ""))
    out.append("")
    out.append("---")
    out.append("")
    out.append(f"*Sources: notes w{week}.pdf | lecture notes | mock exam analysis*")
    
    return "\n".join(out)


# ─── MCQ FORMATTER ─────────────────────────────────────────────────────────
def format_mcq(q, num, show_source=True):
    opts = q.get("options", {})
    answer = q.get("answer", "?")
    difficulty = q.get("difficulty", "Medium")
    topic = q.get("topic", "")
    explanation = q.get("explanation", f"Refer to course material on {topic}." if topic else "Refer to course material.")

    src_line = ""
    if show_source and q.get("source"):
        src_line = f" | **Source:** `{q['source']}`"

    return (
        f"### Q{num}. {q['text']}\n\n"
        f"- **A)** {opts.get('A', '')}\n"
        f"- **B)** {opts.get('B', '')}\n"
        f"- **C)** {opts.get('C', '')}\n"
        f"- **D)** {opts.get('D', '')}\n\n"
        f"<details>\n<summary>✅ Answer & Explanation</summary>\n\n"
        f"**Correct Answer: {answer})** {opts.get(answer, '') if answer != '?' else '(See course material)'}\n\n"
        f"**Explanation:** {explanation}\n\n"
        f"**Difficulty:** {difficulty}{src_line}\n\n"
        f"</details>\n\n---\n\n"
    )


# ─── MCQ GENERATOR ─────────────────────────────────────────────────────────
def generate_mcqs_md(week, mock_questions_by_week, assignment_questions):
    topic = WEEK_TOPICS[week]
    mock_qs = mock_questions_by_week.get(week, [])
    assign_qs = assignment_questions
    generated_qs = GENERATED_MCQS.get(week, [])

    out = []
    out.append(f"# Week {week} — MCQ Practice Bank")
    out.append(f"> **Topic:** {topic} | **Week:** {week} of 12")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 📊 Question Bank Overview")
    out.append("")
    out.append("| Source | Count |")
    out.append("|--------|-------|")
    if mock_qs:
        out.append(f"| Mock Exam Questions (with answers) | {len(mock_qs)} |")
    if assign_qs:
        out.append(f"| Weekly Assignment Questions | {len(assign_qs)} |")
    if generated_qs:
        out.append(f"| Additional Practice Questions | {len(generated_qs)} |")
    out.append(f"| **Total** | **{len(mock_qs)+len(assign_qs)+len(generated_qs)}** |")
    out.append("")

    q_num = 1

    if mock_qs:
        out.append("---")
        out.append("")
        out.append("## 🎯 Section A: Mock Exam Questions")
        out.append("> *Official mock exam questions with verified answers.*")
        out.append("")
        easy = [q for q in mock_qs if q["difficulty"] == "Easy"]
        medium = [q for q in mock_qs if q["difficulty"] == "Medium"]
        hard = [q for q in mock_qs if q["difficulty"] == "Hard"]
        for q in easy + medium + hard:
            out.append(format_mcq(q, q_num, show_source=True))
            q_num += 1

    if assign_qs:
        out.append("---")
        out.append("")
        out.append("## 📝 Section B: Weekly Assignment Questions")
        out.append("> *Official course assignment questions.*")
        out.append("")
        for q in assign_qs:
            q_copy = dict(q)
            q_copy["answer"] = "?"
            q_copy["explanation"] = f"Review course material on {topic} for the answer."
            out.append(format_mcq(q_copy, q_num, show_source=False))
            q_num += 1

    if generated_qs:
        out.append("---")
        out.append("")
        out.append("## 🔄 Section C: Additional Practice Questions")
        out.append("> *Concept-based questions from course material analysis.*")
        out.append("")
        for q in generated_qs:
            q_copy = dict(q)
            q_copy["source"] = f"Week {week} Notes"
            out.append(format_mcq(q_copy, q_num, show_source=False))
            q_num += 1

    out.append("---")
    out.append("")
    out.append("## 📌 Quick Revision Summary")
    out.append("")
    out.append(f"**Total questions: {q_num-1}** | Topic: {topic}")
    out.append("")
    out.append("**Frequently Asked Concepts:**")
    out.append("")
    for p in WEEK_FREQUENTLY_ASKED.get(week, [])[:5]:
        out.append(f"- {p}")
    out.append("")

    return "\n".join(out)



# ─── SUMMARY GENERATOR ─────────────────────────────────────────────────────
def generate_summary(mock_by_week, all_assignment_qs):
    key_themes = {
        1: "BD vs Sales vs Marketing; 8 Demand States; Strategy Framework",
        2: "Growth Formula (POC); SMART Goals; BD Cases (Nirma, Honda)",
        3: "Industry Evolution; Porter's Five Forces; Conglomerates",
        4: "Market Analysis; Demand Cascade; Forecasting Methods",
        5: "Customer vs Consumer; B2B vs B2C; Buying Centre",
        6: "STP Framework; Market Segmentation; Positioning",
        7: "Brand Equity; Brand Architecture; Pharma Branding",
        8: "IT Start-up Strategy; Happiest Minds; Digital-Native",
        9: "Subsidiaries; JVs; Corporate Structure",
        10: "Value Chain; Outsourcing vs Offshoring; Negotiation",
        11: "Growth Strategies; PLC; Industry Life Cycle",
        12: "Pharma Transformation; Orchid Chemicals; API Strategy",
    }
    
    out = []
    out.append("# 📊 Global Study Summary — Business Development: From Start to Scale")
    out.append("")
    out.append("> **Course:** Business Development: From Start to Scale | **All 12 Weeks**")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 📅 Week-by-Week Topics Overview")
    out.append("")
    out.append("| Week | Topic | Key Themes |")
    out.append("|------|-------|------------|")
    for w in range(1, 13):
        out.append(f"| **Week {w}** | {WEEK_TOPICS[w]} | {key_themes[w]} |")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 🏆 Top 25 Most Important Concepts")
    out.append("")
    concepts = [
        ("Business Development (BD)", "W1", "Core definition — appears in every exam"),
        ("Sustainable Growth Formula (POC)", "W2", "Foundation of success analysis"),
        ("Sales vs Marketing vs BD", "W1", "Distinguishing these 3 is a frequent exam trap"),
        ("8 States of Demand", "W1", "Specific definitions tested repeatedly"),
        ("SMART Goals", "W2", "Frequently tested with wrong alternatives as distractors"),
        ("Strategy Roll-out (Plans & Projects)", "W1", "Common distractor: goals or targets"),
        ("STP Framework", "W6", "Foundational marketing framework"),
        ("Brand Equity", "W7", "Multi-component concept tested from various angles"),
        ("Porter's Five Forces", "W3", "Classic strategy framework"),
        ("Value Chain", "W10", "Primary vs Support activities tested"),
        ("Product Life Cycle (PLC)", "W11", "Stage characteristics frequently tested"),
        ("Customer vs Consumer", "W5", "Simple distinction, frequently confused"),
        ("Demand Cascade", "W4", "Funnel from potential to actual sales"),
        ("B2B vs B2C", "W5", "Decision-making characteristics differ significantly"),
        ("Outsourcing vs Offshoring", "W10", "Definitions frequently swapped"),
        ("Strategic Adjacency", "W2/W3", "Related vs unrelated expansion"),
        ("Market Segmentation Types (DGPB)", "W6", "Demographic, Geographic, Psychographic, Behavioral"),
        ("Nirma Case Study", "W2", "Illustrates mass-market disruption strategy"),
        ("Inverted Pyramid Model", "W1/W5", "Customers at the top"),
        ("Competitive Turbulence", "W11", "Occurs in Maturity (not Growth) phase"),
        ("Joint Ventures vs Subsidiaries", "W9", "Ownership and control distinctions"),
        ("Dual Concerns Model", "W10", "Win-Win = high concern for both parties"),
        ("Basic vs Applied Research", "W10", "R&D spectrum with timeline differences"),
        ("Follower Strategy", "W11", "Fragmented market, low returns — not monopoly"),
        ("Structural Barriers", "W1/W4", "Defensive capabilities vs external regulations"),
    ]
    out.append("| # | Concept | Week(s) | Why Important |")
    out.append("|---|---------|---------|---------------|")
    for i, (concept, weeks, reason) in enumerate(concepts, 1):
        out.append(f"| {i} | **{concept}** | {weeks} | {reason} |")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 🔁 Top Repeated Questions Across All Weeks")
    out.append("")
    out.append("### Pattern 1: Definition Questions")
    out.append("- *What is Business Development?* → Creating strategic partnerships for long-term value")
    out.append("- *What is Brand Equity?* → Premium value over generic equivalent")
    out.append("- *What is Cultural Blinds?* → Mindsets blocking cross-cultural interaction")
    out.append("- *What is a Stuck Industry?* → Fragmented + fails to evolve")
    out.append("")
    out.append("### Pattern 2: Distinguishing Similar Concepts")
    out.append("- Sales vs Marketing vs BD")
    out.append("- Customer vs Consumer")
    out.append("- Outsourcing vs Offshoring")
    out.append("- JV vs Subsidiary")
    out.append("- Basic vs Applied vs Developmental Research")
    out.append("")
    out.append("### Pattern 3: 'Which is NOT' Questions")
    out.append("- Which is NOT an endgame strategy? → **Innovation** (correct: Leadership, Niche, Harvesting, Divestment)")
    out.append("- Which is NOT a state of demand? → **Hyper Demand**")
    out.append("")
    out.append("### Pattern 4: Stage/Phase Identification")
    out.append("- Competitive Turbulence → **Maturity** phase")
    out.append("- First-mover advantage → **Introduction** phase")
    out.append("")
    out.append("### Pattern 5: Case Study Application")
    out.append("- Nirma → Mass-market disruption via price + promotion")
    out.append("- Honda → Autonomous Localization")
    out.append("- Happiest Minds → Digital-native IT startup")
    out.append("- Orchid Chemicals → Niche + technology pharma transformation")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## ⚠️ Common Traps & Tricky Questions")
    out.append("")
    traps = [
        ("Strategy roll-out unit", "Goals / Targets", "**Plans & Projects**", "W1"),
        ("Ford Model T", "Product Diversity", "**Product Standardisation**", "W1"),
        ("SMART goals", "Simple/Sustainable", "**Specific**", "W2"),
        ("Strategic marketing duration", "Short-term", "**Medium and Long-term (2-3 years)**", "W1"),
        ("Negative Demand", "Deviant / Latent", "**Consumers dislike & avoid**", "W1"),
        ("BD seeks to achieve", "Immediate sales", "**Long-term partnerships**", "W1"),
        ("Endgame strategy NOT in list", "Leadership/Niche", "**Innovation** (not an endgame strategy)", "W11"),
        ("Competitive Turbulence phase", "Growth", "**Maturity**", "W11"),
        ("Win-Win in Dual Concerns", "Low-High or High-Low", "**High concern for BOTH**", "W10"),
        ("Outsourcing vs Offshoring", "Often swapped", "Out=3rd party, Off=another country", "W10"),
        ("Premium pricing works for", "Cost-competitive firms", "**Differentiated firms**", "W4"),
        ("Demand forecast under disruption", "Linear modelling", "**Expert opinions + simulations**", "W4"),
        ("Test marketing stage", "Concept or prototype", "**Fully finished product**", "W4"),
        ("Conglomerate limitation", "Only conglomerates diversify", "**ANY company** can diversify", "W1"),
    ]
    out.append("| Trap | Wrong Choice | Correct Choice | Week |")
    out.append("|------|-------------|----------------|------|")
    for trap, wrong, correct, week in traps:
        out.append(f"| {trap} | {wrong} | {correct} | {week} |")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 🔑 Global Keyword List")
    out.append("")
    out.append("**Core BD:** Business Development · Strategic Partnerships · Long-term Value · Sales · Marketing · Strategy")
    out.append("")
    out.append("**Marketing:** STP · Segmentation · Targeting · Positioning · Market Share · Demand Cascade · Brand Equity · NPS")
    out.append("")
    out.append("**Frameworks:** Porter's Five Forces · PESTLE · SWOT · BCG Matrix · Ansoff Matrix · Value Chain")
    out.append("")
    out.append("**Operations:** Outsourcing · Offshoring · Subsidiary · Joint Venture · R&D · BATNA · Dual Concerns Model")
    out.append("")
    out.append("**Customer:** Customer vs Consumer · B2B · B2C · Derived Demand · Buying Centre · Brand Architecture")
    out.append("")
    out.append("**Growth:** Sustainable Growth · Product Innovation · Operational Excellence · Customer Fulfillment")
    out.append("PLC · Fragmented Industry · Stuck Industry · Followership · Endgame Strategy · Strategic Adjacency")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 🎯 Exam Strategy")
    out.append("")
    out.append("### Before the Exam")
    out.append("1. **Review Week 1 thoroughly** — foundation and questions appear in every mock exam")
    out.append("2. **Master the definitions** — most traps involve subtle definitional differences")
    out.append("3. **Study case studies** — Nirma, Honda, Happiest Minds, Orchid each teach a strategic principle")
    out.append("4. **Review NOT questions** — memorize which options do NOT belong to each framework")
    out.append("")
    out.append("### During the Exam")
    out.append("1. **Read all options** — distractors are crafted to sound correct")
    out.append("2. **Identify question type:** Definition / Distinction / Stage / Case / Framework")
    out.append("3. **Use elimination** — remove obviously wrong options first")
    out.append("4. **Trust frequency patterns** — strategically sound answers are usually correct")
    out.append("")
    out.append("### High-Confidence Topics")
    out.append("- Week 1: BD definitions, 8 demand states, strategy roll-out")
    out.append("- Week 2: POC formula, SMART goals, Nirma case")
    out.append("- Week 10: Outsourcing/Offshoring, R&D types, Dual Concerns Model")
    out.append("- Week 11: PLC stages, Competitive Turbulence, endgame strategies")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## ⚡ High-Frequency Answers Quick Reference")
    out.append("")
    ref = [
        ("BD seeks to achieve", "**Long-term partnerships**"),
        ("Strategic marketing time", "**Medium and long term (2-3 years)**"),
        ("Strategy rolled out as", "**Plans and Projects**"),
        ("Negative demand", "Consumers **dislike and avoid** the product"),
        ("Marketing effectiveness key component", "**Advertising and Communication**"),
        ("Ford Model T", "**Product Standardisation**"),
        ("Any company diversify?", "**Yes, any company**"),
        ("Sustainable Growth Formula", "**Product Innovation + Operational Excellence + Customer Fulfillment**"),
        ("SMART =", "**Specific, Measurable, Achievable, Relevant, Time-bound**"),
        ("Nirma case lesson", "**Affordable pricing + targeted promotion = mass-market**"),
        ("Customer vs Consumer", "Customer = **buys**; Consumer = **uses**"),
        ("STP sequence", "**Segment → Target → Position**"),
        ("Inverted Pyramid top", "**Customers**"),
        ("Competitive Turbulence phase", "**Maturity**"),
        ("Win-Win negotiation", "**High concern for BOTH self and others**"),
        ("Outsourcing = ", "**Third-party contractor**"),
        ("Offshoring = ", "**Moving function to another country**"),
        ("Basic Research", "**Pure knowledge, very long timeline**"),
        ("Endgame strategies", "Leadership, Niche, Harvesting, Divestment (**NOT Innovation**)"),
        ("Stuck Industry", "**Fragmented + fails to evolve**"),
        ("Follower strategy", "**Fragmented market, cost leadership, low returns**"),
        ("Structural Barriers", "**Defensive capabilities** (not regulations)"),
        ("Brand Equity", "**Premium value over generic equivalent**"),
        ("Cultural Blinds", "**Mindsets blocking cross-cultural interaction**"),
        ("Test marketing stage", "**Fully finished product**"),
    ]
    out.append("| Question Pattern | Answer |")
    out.append("|-----------------|--------|")
    for q, a in ref:
        out.append(f"| {q} | {a} |")
    out.append("")
    out.append("---")
    out.append("")
    out.append("*Generated from: 5 unique mock exams (150 questions), 11 weekly assignments (110 questions),*")
    out.append("*12 notes PDFs, and comprehensive lecture notes — covering all 12 weeks.*")
    
    return "\n".join(out)


# ─── MAIN ───────────────────────────────────────────────────────────────────
def main():
    print("Loading mock exam questions...")
    mock_by_week = load_all_mock_questions()
    print(f"  Weeks covered: {sorted(mock_by_week.keys())}")
    
    print("Loading assignment questions...")
    all_assign = {}
    for w in range(1, 12):
        qs = parse_assignment(w)
        all_assign[w] = qs
        print(f"  Week {w}: {len(qs)} questions")
    
    print("Generating study materials...")
    for week in range(1, 13):
        week_dir = os.path.join(OUT_DIR, f"Week_{week}")
        os.makedirs(week_dir, exist_ok=True)
        
        print(f"\n  Week {week}: {WEEK_TOPICS[week]}")
        notes_text = extract_notes_pdf(week)
        lecture_notes = read_lecture_notes(week)
        
        notes_content = generate_notes_md(week, notes_text, lecture_notes)
        with open(os.path.join(week_dir, "notes.md"), "w", encoding="utf-8") as f:
            f.write(notes_content)
        print(f"    notes.md written ({len(notes_content):,} chars)")
        
        assign_qs = all_assign.get(week, [])
        mcqs_content = generate_mcqs_md(week, mock_by_week, assign_qs)
        with open(os.path.join(week_dir, "mcqs.md"), "w", encoding="utf-8") as f:
            f.write(mcqs_content)
        
        mock_c = len(mock_by_week.get(week, []))
        gen_c = len(GENERATED_MCQS.get(week, []))
        print(f"    mcqs.md written ({mock_c} mock + {len(assign_qs)} assignment + {gen_c} generated)")
    
    print("\nGenerating global summary...")
    all_assign_flat = [q for qs in all_assign.values() for q in qs]
    summary = generate_summary(mock_by_week, all_assign_flat)
    with open(os.path.join(OUT_DIR, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"  summary.md written ({len(summary):,} chars)")
    
    print("\nDone! Files in:", OUT_DIR)


if __name__ == "__main__":
    main()
