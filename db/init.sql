-- Create database and user
CREATE DATABASE leadnest;
CREATE USER leadnest_user WITH PASSWORD 'leadnest_password';
GRANT ALL PRIVILEGES ON DATABASE leadnest TO leadnest_user;

-- Connect to the database
\c leadnest;

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO leadnest_user;
