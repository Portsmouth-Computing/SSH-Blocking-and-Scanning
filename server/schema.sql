CREATE TABLE IF NOT EXISTS ip_storage (
    ip CIDR PRIMARY KEY,
    country_code TEXT CHECK (char_length(country_code) = 2),

    accessed BIGINT DEFAULT 1,
    last_updated TIMESTAMP DEFAULT now()
);
