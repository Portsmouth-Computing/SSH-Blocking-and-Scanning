CREATE TABLE IF NOT EXISTS ip_storage (
    ip INET PRIMARY KEY,
    country_code TEXT CHECK (char_length(country_code) <= 2),

    accessed BIGINT DEFAULT 1,
    city TEXT check (char_length(city) <= 50),
    region TEXT check (char_length(region) <= 50),
    org TEXT check (char_length(org) <= 50),
    loc TEXT check (char_length(loc) <= 20),
    last_updated TIMESTAMP DEFAULT now()
);
