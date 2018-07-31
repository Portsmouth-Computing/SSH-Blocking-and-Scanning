CREATE TABLE IF NOT EXISTS ip_storage (
    ip varchar(15) PRIMARY KEY,
    country varchar(2),
    last_updated_time int,
    amount_checked bigint
);
