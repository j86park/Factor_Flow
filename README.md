# Factor_Flow

Factor Flow is an end-to-end quantitative investment platform that surfaces data-driven insights through three core analytical engines:

Graph-Based Alpha Generation: A Graph Attention Network (GAT) implemented in PyTorch Geometric that models the market as a correlation-based graph, learning stock representations through multi-head attention to predict forward returns.

Statistical Factor Engine: A high-performance engine computing SOTA quantitative metrics, including asymmetric (upside) beta, idiosyncratic volatility, and long-term momentum across the full stock universe.

Thematic RAG Pipeline: A "Retrieval-Augmented Classification" system that uses pgvector semantic search and GPT-4 verification to identify pure-play stocks in emerging themes (e.g., AI Infrastructure, Uranium) with 70% higher accuracy than vector-only methods.

Tech Stack: Python (FastAPI), PyTorch/GNN, Supabase (PostgreSQL + pgvector), React/TypeScript, and OpenAI.
