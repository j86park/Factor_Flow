# factors.py

# ==========================================
# MASTER FACTOR LIST
# Formatted for Supabase Schema:
# name (text), type (text), description (text), logic_config (jsonb), is_active (bool)
# ==========================================

ALL_FACTORS = [
    # ==========================================
    # 1. THEMATIC FACTORS
    # type: "THEMATIC"
    # logic_config: { "prompt_text": "..." }
    # ==========================================
    
    # --- AI & COMPUTING ---
    {
        "name": "AI Adopters Early",
        "type": "THEMATIC",
        "description": "Non-tech companies deploying AI to improve margins and productivity. Efficiency gains from AI tools.",
        "logic_config": {"prompt_text": "Non-tech companies deploying AI to improve margins and productivity. Efficiency gains from AI tools."},
        "is_active": True
    },
    {
        "name": "AI Private Credit",
        "type": "THEMATIC",
        "description": "Private credit funds or BDCs with exposure to private debt financing specifically in the AI sector.",
        "logic_config": {"prompt_text": "Private credit funds or BDCs with exposure to private debt financing specifically in the AI sector."},
        "is_active": True
    },
    {
        "name": "AI Theme Winners",
        "type": "THEMATIC",
        "description": "Direct beneficiaries of AI adoption including infrastructure, chips, cooling, and cabling.",
        "logic_config": {"prompt_text": "Direct beneficiaries of AI adoption including infrastructure, chips, cooling, and cabling."},
        "is_active": True
    },
    {
        "name": "AI Winners (Second Order)",
        "type": "THEMATIC",
        "description": "Second-order AI beneficiaries beyond chips and cloud, such as data centers, cybersecurity, and services.",
        "logic_config": {"prompt_text": "Second-order AI beneficiaries beyond chips and cloud, such as data centers, cybersecurity, and services."},
        "is_active": True
    },
    {
        "name": "Chips AI",
        "type": "THEMATIC",
        "description": "Semiconductor companies focused on AI, specifically leveraging datacenter GPU demand.",
        "logic_config": {"prompt_text": "Semiconductor companies focused on AI, specifically leveraging datacenter GPU demand."},
        "is_active": True
    },
    {
        "name": "Computing Edge",
        "type": "THEMATIC",
        "description": "Companies building edge computing and distributed AI infrastructure (processing closer to data sources).",
        "logic_config": {"prompt_text": "Companies building edge computing and distributed AI infrastructure (processing closer to data sources)."},
        "is_active": True
    },
    {
        "name": "OAI Ecosystem",
        "type": "THEMATIC",
        "description": "Companies benefiting from OpenAI's specific growth, partnerships, or Project Stargate.",
        "logic_config": {"prompt_text": "Companies benefiting from OpenAI's specific growth, partnerships, or Project Stargate."},
        "is_active": True
    },
    {
        "name": "Power AI Theme",
        "type": "THEMATIC",
        "description": "Utilities and grid infrastructure providers specifically serving datacenter load growth.",
        "logic_config": {"prompt_text": "Utilities and grid infrastructure providers specifically serving datacenter load growth."},
        "is_active": True
    },
    {
        "name": "Team TPU",
        "type": "THEMATIC",
        "description": "Companies leveraging Google's Tensor Processing Units (TPUs). AI hardware and cloud service beneficiaries.",
        "logic_config": {"prompt_text": "Companies leveraging Google's Tensor Processing Units (TPUs). AI hardware and cloud service beneficiaries."},
        "is_active": True
    },
    {
        "name": "Tech Cutting Edge",
        "type": "THEMATIC",
        "description": "Next-generation technology companies pushing boundaries. High-growth, high-volatility innovation plays.",
        "logic_config": {"prompt_text": "Next-generation technology companies pushing boundaries. High-growth, high-volatility innovation plays."},
        "is_active": True
    },
    {
        "name": "Quantum Spec",
        "type": "THEMATIC",
        "description": "Quantum computing companies in early commercialization. Speculative, long-duration bets.",
        "logic_config": {"prompt_text": "Quantum computing companies in early commercialization. Speculative, long-duration bets."},
        "is_active": True
    },
    {
        "name": "SaaS Full Universe",
        "type": "THEMATIC",
        "description": "All software-as-a-service companies. Secular shift from on-premise to cloud.",
        "logic_config": {"prompt_text": "All software-as-a-service companies. Secular shift from on-premise to cloud."},
        "is_active": True
    },
    {
        "name": "Software Small Biz",
        "type": "THEMATIC",
        "description": "SMB-focused software and vertical SaaS. Smaller TAM but stickier customers.",
        "logic_config": {"prompt_text": "SMB-focused software and vertical SaaS. Smaller TAM but stickier customers."},
        "is_active": True
    },

    # --- CRYPTO & BLOCKCHAIN ---
    {
        "name": "Bitcoin Datacenter Plays",
        "type": "THEMATIC",
        "description": "Bitcoin mining companies pivoting infrastructure to host AI datacenters.",
        "logic_config": {"prompt_text": "Bitcoin mining companies pivoting infrastructure to host AI datacenters."},
        "is_active": True
    },
    {
        "name": "Ethereum",
        "type": "THEMATIC",
        "description": "Companies with direct balance sheet exposure to Ethereum or building on the Ethereum smart contract platform.",
        "logic_config": {"prompt_text": "Companies with direct balance sheet exposure to Ethereum or building on the Ethereum smart contract platform."},
        "is_active": True
    },
    {
        "name": "Stablecoins",
        "type": "THEMATIC",
        "description": "Dollar-pegged cryptocurrency issuers and crypto payment infrastructure.",
        "logic_config": {"prompt_text": "Dollar-pegged cryptocurrency issuers and crypto payment infrastructure."},
        "is_active": True
    },

    # --- ROBOTICS & SPACE ---
    {
        "name": "Humanoids China",
        "type": "THEMATIC",
        "description": "Chinese robotics companies specifically developing humanoid form factors. Moonshot exposure.",
        "logic_config": {"prompt_text": "Chinese robotics companies specifically developing humanoid form factors. Moonshot exposure."},
        "is_active": True
    },
    {
        "name": "Robotics",
        "type": "THEMATIC",
        "description": "Next-generation automation and AI-driven robotics (excluding legacy industrial).",
        "logic_config": {"prompt_text": "Next-generation automation and AI-driven robotics (excluding legacy industrial)."},
        "is_active": True
    },
    {
        "name": "Space Mob",
        "type": "THEMATIC",
        "description": "Commercial space exploration, satellite infrastructure, and aerospace innovation.",
        "logic_config": {"prompt_text": "Commercial space exploration, satellite infrastructure, and aerospace innovation."},
        "is_active": True
    },
    {
        "name": "UAV Drones",
        "type": "THEMATIC",
        "description": "Drone manufacturers and autonomous aerial vehicle exposure.",
        "logic_config": {"prompt_text": "Drone manufacturers and autonomous aerial vehicle exposure."},
        "is_active": True
    },

    # --- ENERGY & COMMODITIES ---
    {
        "name": "Agg",
        "type": "THEMATIC",
        "description": "Agricultural commodities, farming equipment, and food security. Weather-dependent.",
        "logic_config": {"prompt_text": "Agricultural commodities, farming equipment, and food security. Weather-dependent."},
        "is_active": True
    },
    {
        "name": "Drillers Energy",
        "type": "THEMATIC",
        "description": "Exploration & production (E&P) companies focused on drilling. Pure-play leverage to oil & gas prices.",
        "logic_config": {"prompt_text": "Exploration & production (E&P) companies focused on drilling. Pure-play leverage to oil & gas prices."},
        "is_active": True
    },
    {
        "name": "Dr Copper",
        "type": "THEMATIC",
        "description": "Copper miners and refiners. Proxy for global industrial demand.",
        "logic_config": {"prompt_text": "Copper miners and refiners. Proxy for global industrial demand."},
        "is_active": True
    },
    {
        "name": "Nuclear",
        "type": "THEMATIC",
        "description": "Uranium miners and nuclear power generators. Clean baseload power.",
        "logic_config": {"prompt_text": "Uranium miners and nuclear power generators. Clean baseload power."},
        "is_active": True
    },
    {
        "name": "Minerals USG Target",
        "type": "THEMATIC",
        "description": "Critical minerals (lithium, cobalt, rare earths) targeted by US government strategic security acts.",
        "logic_config": {"prompt_text": "Critical minerals (lithium, cobalt, rare earths) targeted by US government strategic security acts."},
        "is_active": True
    },
    {
        "name": "Platinum",
        "type": "THEMATIC",
        "description": "Platinum metal miners. Exposure to auto catalytic converter demand.",
        "logic_config": {"prompt_text": "Platinum metal miners. Exposure to auto catalytic converter demand."},
        "is_active": True
    },
    {
        "name": "Refiners Energy",
        "type": "THEMATIC",
        "description": "Companies processing crude into gasoline/diesel. Benefit from wide crack spreads.",
        "logic_config": {"prompt_text": "Companies processing crude into gasoline/diesel. Benefit from wide crack spreads."},
        "is_active": True
    },
    {
        "name": "Renewables",
        "type": "THEMATIC",
        "description": "Solar, wind, and clean energy transition companies.",
        "logic_config": {"prompt_text": "Solar, wind, and clean energy transition companies."},
        "is_active": True
    },
    {
        "name": "Steel",
        "type": "THEMATIC",
        "description": "Steel producers and metal manufacturers. Cyclical exposure to construction and manufacturing.",
        "logic_config": {"prompt_text": "Steel producers and metal manufacturers. Cyclical exposure to construction and manufacturing."},
        "is_active": True
    },
    {
        "name": "Uranium Big Beta",
        "type": "THEMATIC",
        "description": "High-beta uranium mining stocks. Amplified leverage to nuclear fuel demand.",
        "logic_config": {"prompt_text": "High-beta uranium mining stocks. Amplified leverage to nuclear fuel demand."},
        "is_active": True
    },
    {
        "name": "Water",
        "type": "THEMATIC",
        "description": "Water utilities and infrastructure. Scarcity and safety themes.",
        "logic_config": {"prompt_text": "Water utilities and infrastructure. Scarcity and safety themes."},
        "is_active": True
    },

    # --- MACRO, POLICY & GOV ---
    {
        "name": "Defense EU",
        "type": "THEMATIC",
        "description": "European defense contractors and suppliers benefiting from increased NATO spending.",
        "logic_config": {"prompt_text": "European defense contractors and suppliers benefiting from increased NATO spending."},
        "is_active": True
    },
    {
        "name": "DOGE (Gov Efficiency)",
        "type": "THEMATIC",
        "description": "Beneficiaries of government efficiency initiatives, automation, and outsourcing (GovTech).",
        "logic_config": {"prompt_text": "Beneficiaries of government efficiency initiatives, automation, and outsourcing (GovTech)."},
        "is_active": True
    },
    {
        "name": "MAHA RFK",
        "type": "THEMATIC",
        "description": "Make America Healthy Again policy beneficiaries. Wellness focus vs Big Pharma/Food.",
        "logic_config": {"prompt_text": "Make America Healthy Again policy beneficiaries. Wellness focus vs Big Pharma/Food."},
        "is_active": True
    },
    {
        "name": "Exposure China",
        "type": "THEMATIC",
        "description": "Companies with significant revenue exposure to China. Proxy for China growth/policy.",
        "logic_config": {"prompt_text": "Companies with significant revenue exposure to China. Proxy for China growth/policy."},
        "is_active": True
    },
    {
        "name": "Exposure European",
        "type": "THEMATIC",
        "description": "Companies with significant revenue exposure to Europe.",
        "logic_config": {"prompt_text": "Companies with significant revenue exposure to Europe."},
        "is_active": True
    },
    {
        "name": "Onshoring",
        "type": "THEMATIC",
        "description": "Companies benefiting from manufacturing returning to the US. Reshoring and friend-shoring plays.",
        "logic_config": {"prompt_text": "Companies benefiting from manufacturing returning to the US. Reshoring and friend-shoring plays."},
        "is_active": True
    },
    {
        "name": "Tax Beneficiaries",
        "type": "THEMATIC",
        "description": "Companies with significant sensitivity to corporate tax rate reductions.",
        "logic_config": {"prompt_text": "Companies with significant sensitivity to corporate tax rate reductions."},
        "is_active": True
    },
    {
        "name": "Tariffs China",
        "type": "THEMATIC",
        "description": "Companies sensitive to China trade policy and tariffs.",
        "logic_config": {"prompt_text": "Companies sensitive to China trade policy and tariffs."},
        "is_active": True
    },
    {
        "name": "Tariffs Mexico",
        "type": "THEMATIC",
        "description": "Companies sensitive to Mexico trade policy (USMCA/Nearshoring).",
        "logic_config": {"prompt_text": "Companies sensitive to Mexico trade policy (USMCA/Nearshoring)."},
        "is_active": True
    },

    # --- CONSUMER & CYCLICALS ---
    {
        "name": "Airlines",
        "type": "THEMATIC",
        "description": "Passenger and cargo airline operators. Sensitive to travel demand and fuel costs.",
        "logic_config": {"prompt_text": "Passenger and cargo airline operators. Sensitive to travel demand and fuel costs."},
        "is_active": True
    },
    {
        "name": "Autos",
        "type": "THEMATIC",
        "description": "Automobile manufacturers and parts suppliers.",
        "logic_config": {"prompt_text": "Automobile manufacturers and parts suppliers."},
        "is_active": True
    },
    {
        "name": "Construction Non-Ressy",
        "type": "THEMATIC",
        "description": "Commercial and industrial construction companies (Non-residential building activity).",
        "logic_config": {"prompt_text": "Commercial and industrial construction companies (Non-residential building activity)."},
        "is_active": True
    },
    {
        "name": "Consumer Domestic vs Global",
        "type": "THEMATIC",
        "description": "US-focused vs globally exposed consumer companies.",
        "logic_config": {"prompt_text": "US-focused vs globally exposed consumer companies."},
        "is_active": True
    },
    {
        "name": "Credit Cards",
        "type": "THEMATIC",
        "description": "Payment networks and credit card issuers. Consumer spending proxy.",
        "logic_config": {"prompt_text": "Payment networks and credit card issuers. Consumer spending proxy."},
        "is_active": True
    },
    {
        "name": "E-Comm",
        "type": "THEMATIC",
        "description": "E-commerce platforms and online retailers.",
        "logic_config": {"prompt_text": "E-commerce platforms and online retailers."},
        "is_active": True
    },
    {
        "name": "GLP-1 Winners",
        "type": "THEMATIC",
        "description": "Obesity drug manufacturers and direct supply chain enablers.",
        "logic_config": {"prompt_text": "Obesity drug manufacturers and direct supply chain enablers."},
        "is_active": True
    },
    {
        "name": "GLP-1 Losers",
        "type": "THEMATIC",
        "description": "Snack food, sugary drinks, and medical devices negatively correlated with obesity drug adoption.",
        "logic_config": {"prompt_text": "Snack food, sugary drinks, and medical devices negatively correlated with obesity drug adoption."},
        "is_active": True
    },
    {
        "name": "Homebuilders US",
        "type": "THEMATIC",
        "description": "US residential construction companies sensitive to mortgage rates.",
        "logic_config": {"prompt_text": "US residential construction companies sensitive to mortgage rates."},
        "is_active": True
    },
    {
        "name": "Hospitals",
        "type": "THEMATIC",
        "description": "Healthcare facility operators exposed to patient volumes and reimbursement rates.",
        "logic_config": {"prompt_text": "Healthcare facility operators exposed to patient volumes and reimbursement rates."},
        "is_active": True
    },
    {
        "name": "Las Vegas Exposure",
        "type": "THEMATIC",
        "description": "Casinos and hotels with significant revenue from the Las Vegas strip.",
        "logic_config": {"prompt_text": "Casinos and hotels with significant revenue from the Las Vegas strip."},
        "is_active": True
    },
    {
        "name": "Luxury",
        "type": "THEMATIC",
        "description": "High-end discretionary goods. Proxy for the wealth effect.",
        "logic_config": {"prompt_text": "High-end discretionary goods. Proxy for the wealth effect."},
        "is_active": True
    },
    {
        "name": "Online Gambling",
        "type": "THEMATIC",
        "description": "Sports betting and prediction market platforms.",
        "logic_config": {"prompt_text": "Sports betting and prediction market platforms."},
        "is_active": True
    },
    {
        "name": "MedTech",
        "type": "THEMATIC",
        "description": "Medical device manufacturers. Stable growth tied to aging demographics.",
        "logic_config": {"prompt_text": "Medical device manufacturers. Stable growth tied to aging demographics."},
        "is_active": True
    },
    {
        "name": "Retail Brick & Mortar",
        "type": "THEMATIC",
        "description": "Physical retail stores competing with e-commerce. Foot traffic dependent.",
        "logic_config": {"prompt_text": "Physical retail stores competing with e-commerce. Foot traffic dependent."},
        "is_active": True
    },
    {
        "name": "Restaurants",
        "type": "THEMATIC",
        "description": "Restaurant chains and food service. Discretionary spending indicator.",
        "logic_config": {"prompt_text": "Restaurant chains and food service. Discretionary spending indicator."},
        "is_active": True
    },

    # ==========================================
    # 2. STATISTICAL FACTORS
    # type: "STATISTICAL"
    # logic_config: { "metric": ..., "rule": ..., "value": ... }
    # ==========================================

    # --- MOMENTUM ---
    {
        "name": "Momentum Long",
        "type": "STATISTICAL",
        "description": "Top 10% 12-month return",
        "logic_config": {"metric": "return_12m", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Momentum Short",
        "type": "STATISTICAL",
        "description": "Bottom 10% 12-month return",
        "logic_config": {"metric": "return_12m", "rule": "bottom_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Momo 3m Long",
        "type": "STATISTICAL",
        "description": "Top 10% 3-month return",
        "logic_config": {"metric": "return_3m", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Momo 3m Short",
        "type": "STATISTICAL",
        "description": "Bottom 10% 3-month return",
        "logic_config": {"metric": "return_3m", "rule": "bottom_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Momo NDX Intraday",
        "type": "STATISTICAL",
        "description": "Nasdaq stocks with highest daily range",
        "logic_config": {"metric": "intraday_vol", "rule": "top_percentile", "value": 0.05, "universe": "NDX"},
        "is_active": True
    },

    # --- VOLATILITY ---
    {
        "name": "Vol High",
        "type": "STATISTICAL",
        "description": "Highest realized volatility",
        "logic_config": {"metric": "volatility_90d", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Vol Low",
        "type": "STATISTICAL",
        "description": "Lowest realized volatility",
        "logic_config": {"metric": "volatility_90d", "rule": "bottom_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Vol Low Anti Beta",
        "type": "STATISTICAL",
        "description": "Low Vol + Negative Correlation",
        "logic_config": {"metric": "beta", "rule": "bottom_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Vol Rezzy",
        "type": "STATISTICAL",
        "description": "High residual volatility (non-market risk)",
        "logic_config": {"metric": "idiosyncratic_vol", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },

    # --- BETA / SENSITIVITY ---
    {
        "name": "Beta (High)",
        "type": "STATISTICAL",
        "description": "Beta > 1.5",
        "logic_config": {"metric": "beta", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Beta Upside High",
        "type": "STATISTICAL",
        "description": "Stocks that participate most in market rallies",
        "logic_config": {"metric": "upside_beta", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Cyclicals Big Beta",
        "type": "STATISTICAL",
        "description": "Cyclicals with >1.5 Beta",
        "logic_config": {"metric": "beta", "rule": "greater_than", "value": 1.5},
        "is_active": True
    },

    # --- QUALITY & BALANCE SHEET ---
    {
        "name": "Balance Sheets Best",
        "type": "STATISTICAL",
        "description": "Net Cash / Zero Debt",
        "logic_config": {"metric": "debt_to_equity", "rule": "equals", "value": 0},
        "is_active": True
    },
    {
        "name": "Balance Sheets Weak",
        "type": "STATISTICAL",
        "description": "High Leverage",
        "logic_config": {"metric": "debt_to_equity", "rule": "top_percentile", "value": 0.20},
        "is_active": True
    },
    {
        "name": "ROIC High",
        "type": "STATISTICAL",
        "description": "Top Return on Invested Capital",
        "logic_config": {"metric": "roic", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Quality Low",
        "type": "STATISTICAL",
        "description": "Poor capital efficiency",
        "logic_config": {"metric": "roic", "rule": "bottom_percentile", "value": 0.10},
        "is_active": True
    },

    # --- VALUATION ---
    {
        "name": "Valuation Low",
        "type": "STATISTICAL",
        "description": "Cheapest decile by P/E",
        "logic_config": {"metric": "pe_ratio", "rule": "bottom_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Tech Cash Burn",
        "type": "STATISTICAL",
        "description": "Unprofitable Tech Companies",
        "logic_config": {"metric": "net_income", "rule": "less_than", "value": 0, "filter_sector": "Technology"},
        "is_active": True
    },

    # --- LEVERAGE / FLOWS ---
    {
        "name": "Gas Nat 2X",
        "type": "STATISTICAL",
        "description": "2x Leveraged Nat Gas ETFs",
        "logic_config": {"metric": "leverage_ratio", "rule": "equals", "value": 2, "asset_class": "nat_gas"},
        "is_active": True
    },
    {
        "name": "Inflation 2X",
        "type": "STATISTICAL",
        "description": "2x Leveraged Inflation ETFs",
        "logic_config": {"metric": "leverage_ratio", "rule": "equals", "value": 2, "asset_class": "tips"},
        "is_active": True
    },
    {
        "name": "Buybacks Share",
        "type": "STATISTICAL",
        "description": "Highest net buyback yield",
        "logic_config": {"metric": "buyback_yield", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },
    {
        "name": "Flow Retail",
        "type": "STATISTICAL",
        "description": "High retail buying activity",
        "logic_config": {"metric": "retail_net_flow", "rule": "top_percentile", "value": 0.05},
        "is_active": True
    },

    # --- CROWDING (Requires 13F Data) ---
    {
        "name": "Hedge Fund Crowded",
        "type": "STATISTICAL",
        "description": "Top HF holdings",
        "logic_config": {"metric": "hf_concentration", "rule": "top_percentile", "value": 0.05},
        "is_active": True
    },
    {
        "name": "Shorts Crowded",
        "type": "STATISTICAL",
        "description": "Highest Short Interest %",
        "logic_config": {"metric": "short_interest", "rule": "top_percentile", "value": 0.10},
        "is_active": True
    },

    # ==========================================
    # 3. COMPOSITE FACTORS
    # type: "COMPOSITE"
    # logic_config: { "long_leg": {...}, "short_leg": {...} }
    # ==========================================

    {
        "name": "Growth vs Value",
        "type": "COMPOSITE",
        "description": "Long High Growth - Long Deep Value",
        "logic_config": {
            "long_leg": {"metric": "sales_growth", "rule": "top_percentile", "value": 0.20},
            "short_leg": {"metric": "pe_ratio", "rule": "bottom_percentile", "value": 0.20}
        },
        "is_active": True
    },
    {
        "name": "Discretionary vs Staples",
        "type": "COMPOSITE",
        "description": "Cyclical Consumer vs Defensive Consumer",
        "logic_config": {
            "long_leg": {"sector": "Consumer Discretionary"},
            "short_leg": {"sector": "Consumer Staples"}
        },
        "is_active": True
    },
    {
        "name": "Inflation vs Pricing Pressure",
        "type": "COMPOSITE",
        "description": "Companies passing costs vs companies eating costs",
        "logic_config": {
            "long_leg": {"theme": "Pricing Power"},
            "short_leg": {"theme": "Margin Squeezed"}
        },
        "is_active": True
    },
    {
        "name": "Quality High vs Low",
        "type": "COMPOSITE",
        "description": "Capital Efficiency Spread",
        "logic_config": {
            "long_leg": {"metric": "roic", "rule": "top_percentile", "value": 0.20},
            "short_leg": {"metric": "roic", "rule": "bottom_percentile", "value": 0.20}
        },
        "is_active": True
    },
    {
        "name": "Software vs Semis",
        "type": "COMPOSITE",
        "description": "SaaS vs Chips Spread",
        "logic_config": {
            "long_leg": {"industry": "Software"},
            "short_leg": {"industry": "Semiconductors"}
        },
        "is_active": True
    },
    {
        "name": "Tech New vs Old",
        "type": "COMPOSITE",
        "description": "Innovation vs Legacy Tech",
        "logic_config": {
            "long_leg": {"theme": "Tech Cutting Edge"},
            "short_leg": {"theme": "Tech Sleepy"}
        },
        "is_active": True
    }
]