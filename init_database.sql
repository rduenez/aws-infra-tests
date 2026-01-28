-- Run this SQL script in DBeaver after connecting to create the sample table

-- Create items table for CRUD operations
CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert some sample data
INSERT INTO items (name, description, price, quantity) VALUES
    ('Widget A', 'A fantastic widget for all your needs', 19.99, 100),
    ('Gadget B', 'The latest gadget with amazing features', 49.99, 50),
    ('Tool C', 'Professional grade tool', 99.99, 25);

-- Verify the data
SELECT * FROM items;
