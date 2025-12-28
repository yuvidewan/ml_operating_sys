CREATE TABLE app_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_name VARCHAR(255),
    opened_at DOUBLE NOT NULL
);

CREATE TABLE seq(
    prev VARCHAR(255),
    curr VARCHAR(255),
    prev_closed boolean
)
