-- SQL Schema for Supabase Tables
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor > New Query)

-- Create definitions table


-- Create factors table
CREATE TABLE IF NOT EXISTS factors (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create factor_returns table (for storing time-series return data)
CREATE TABLE IF NOT EXISTS factor_returns (
    id BIGSERIAL PRIMARY KEY,
    factor_id BIGINT REFERENCES factors(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    return_1d NUMERIC(10, 4),
    return_5d NUMERIC(10, 4),
    return_1m NUMERIC(10, 4),
    return_3m NUMERIC(10, 4),
    return_6m NUMERIC(10, 4),
    return_12m NUMERIC(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(factor_id, date)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_factors_category ON factors(category);
CREATE INDEX IF NOT EXISTS idx_factor_returns_factor_id ON factor_returns(factor_id);
CREATE INDEX IF NOT EXISTS idx_factor_returns_date ON factor_returns(date);

-- Enable Row Level Security (RLS) - adjust policies as needed
ALTER TABLE definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE factors ENABLE ROW LEVEL SECURITY;
ALTER TABLE factor_returns ENABLE ROW LEVEL SECURITY;

-- Create policies to allow public read access (adjust based on your security needs)
CREATE POLICY "Allow public read access on definitions" ON definitions
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access on factors" ON factors
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access on factor_returns" ON factor_returns
    FOR SELECT USING (true);

-- Optional: Allow service role to insert/update/delete (for your backend scripts)
-- These policies allow full access when using service_role key
-- Comment out if you want stricter control

-- CREATE POLICY "Allow service role full access on definitions" ON definitions
--     FOR ALL USING (true);

-- CREATE POLICY "Allow service role full access on factors" ON factors
--     FOR ALL USING (true);

-- CREATE POLICY "Allow service role full access on factor_returns" ON factor_returns
--     FOR ALL USING (true);




