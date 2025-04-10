-- Seed data for testing the Family Finance Manager

-- Clear existing data
TRUNCATE users, transactions, goals, goal_participants, goal_contributions, notifications CASCADE;

-- Reset sequences
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE transactions_id_seq RESTART WITH 1;
ALTER SEQUENCE goals_id_seq RESTART WITH 1;
ALTER SEQUENCE goal_contributions_id_seq RESTART WITH 1;
ALTER SEQUENCE notifications_id_seq RESTART WITH 1;

-- Insert users
-- Family 1: Silva
INSERT INTO users (email, hashed_password, full_name, is_active, is_family_head, family_head_id, created_at, updated_at)
VALUES 
('joao.silva@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'João Silva', true, true, NULL, NOW(), NOW()), -- password: password
('maria.silva@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Maria Silva', true, false, 1, NOW(), NOW()),
('pedro.silva@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Pedro Silva', true, false, 1, NOW(), NOW());

-- Family 2: Santos
INSERT INTO users (email, hashed_password, full_name, is_active, is_family_head, family_head_id, created_at, updated_at)
VALUES 
('ana.santos@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Ana Santos', true, true, NULL, NOW(), NOW()),
('carlos.santos@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Carlos Santos', true, false, 4, NOW(), NOW()),
('julia.santos@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Julia Santos', true, false, 4, NOW(), NOW());

-- Insert transactions for Family 1
-- João Silva (Family Head)
INSERT INTO transactions (amount, description, type, category, date, user_id, created_at, updated_at)
VALUES
-- Income
(5000.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '1 month', 1, NOW(), NOW()),
(5000.00, 'Salário', 'income', 'salary', NOW(), 1, NOW(), NOW()),
(1000.00, 'Bônus', 'income', 'bonus', NOW() - INTERVAL '15 days', 1, NOW(), NOW()),
(250.00, 'Dividendos', 'income', 'investment', NOW() - INTERVAL '10 days', 1, NOW(), NOW()),

-- Expenses
(1500.00, 'Aluguel', 'expense', 'housing', NOW() - INTERVAL '25 days', 1, NOW(), NOW()),
(500.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '20 days', 1, NOW(), NOW()),
(300.00, 'Conta de Luz', 'expense', 'utilities', NOW() - INTERVAL '18 days', 1, NOW(), NOW()),
(200.00, 'Internet', 'expense', 'utilities', NOW() - INTERVAL '15 days', 1, NOW(), NOW()),
(800.00, 'Parcela do Carro', 'expense', 'transportation', NOW() - INTERVAL '10 days', 1, NOW(), NOW()),
(150.00, 'Combustível', 'expense', 'transportation', NOW() - INTERVAL '5 days', 1, NOW(), NOW()),
(300.00, 'Jantar fora', 'expense', 'entertainment', NOW() - INTERVAL '3 days', 1, NOW(), NOW());

-- Maria Silva (Spouse)
INSERT INTO transactions (amount, description, type, category, date, user_id, created_at, updated_at)
VALUES
-- Income
(3500.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '1 month', 2, NOW(), NOW()),
(3500.00, 'Salário', 'income', 'salary', NOW(), 2, NOW(), NOW()),
(500.00, 'Freelance', 'income', 'other', NOW() - INTERVAL '15 days', 2, NOW(), NOW()),

-- Expenses
(400.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '22 days', 2, NOW(), NOW()),
(150.00, 'Roupas', 'expense', 'clothing', NOW() - INTERVAL '18 days', 2, NOW(), NOW()),
(200.00, 'Academia', 'expense', 'healthcare', NOW() - INTERVAL '15 days', 2, NOW(), NOW()),
(100.00, 'Livros', 'expense', 'education', NOW() - INTERVAL '10 days', 2, NOW(), NOW()),
(250.00, 'Presente Aniversário', 'expense', 'gifts', NOW() - INTERVAL '5 days', 2, NOW(), NOW()),
(180.00, 'Jantar fora', 'expense', 'entertainment', NOW() - INTERVAL '2 days', 2, NOW(), NOW());

-- Pedro Silva (Son)
INSERT INTO transactions (amount, description, type, category, date, user_id, created_at, updated_at)
VALUES
-- Income
(800.00, 'Mesada', 'income', 'other', NOW() - INTERVAL '1 month', 3, NOW(), NOW()),
(800.00, 'Mesada', 'income', 'other', NOW(), 3, NOW(), NOW()),
(200.00, 'Trabalho temporário', 'income', 'other', NOW() - INTERVAL '15 days', 3, NOW(), NOW()),

-- Expenses
(300.00, 'Material escolar', 'expense', 'education', NOW() - INTERVAL '25 days', 3, NOW(), NOW()),
(150.00, 'Lanche na escola', 'expense', 'food', NOW() - INTERVAL '20 days', 3, NOW(), NOW()),
(200.00, 'Jogos', 'expense', 'entertainment', NOW() - INTERVAL '15 days', 3, NOW(), NOW()),
(100.00, 'Roupas', 'expense', 'clothing', NOW() - INTERVAL '10 days', 3, NOW(), NOW()),
(50.00, 'Cinema', 'expense', 'entertainment', NOW() - INTERVAL '5 days', 3, NOW(), NOW());

-- Insert transactions for Family 2
-- Ana Santos (Family Head)
INSERT INTO transactions (amount, description, type, category, date, user_id, created_at, updated_at)
VALUES
-- Income
(6000.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '1 month', 4, NOW(), NOW()),
(6000.00, 'Salário', 'income', 'salary', NOW(), 4, NOW(), NOW()),
(1500.00, 'Consultoria', 'income', 'other', NOW() - INTERVAL '15 days', 4, NOW(), NOW()),
(300.00, 'Dividendos', 'income', 'investment', NOW() - INTERVAL '10 days', 4, NOW(), NOW()),

-- Expenses
(2000.00, 'Aluguel', 'expense', 'housing', NOW() - INTERVAL '25 days', 4, NOW(), NOW()),
(600.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '20 days', 4, NOW(), NOW()),
(350.00, 'Conta de Luz', 'expense', 'utilities', NOW() - INTERVAL '18 days', 4, NOW(), NOW()),
(250.00, 'Internet', 'expense', 'utilities', NOW() - INTERVAL '15 days', 4, NOW(), NOW()),
(1000.00, 'Parcela do Carro', 'expense', 'transportation', NOW() - INTERVAL '10 days', 4, NOW(), NOW()),
(200.00, 'Combustível', 'expense', 'transportation', NOW() - INTERVAL '5 days', 4, NOW(), NOW()),
(400.00, 'Jantar fora', 'expense', 'entertainment', NOW() - INTERVAL '3 days', 4, NOW(), NOW());

-- Carlos Santos (Spouse)
INSERT INTO transactions (amount, description, type, category, date, user_id, created_at, updated_at)
VALUES
-- Income
(4000.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '1 month', 5, NOW(), NOW()),
(4000.00, 'Salário', 'income', 'salary', NOW(), 5, NOW(), NOW()),
(800.00, 'Freelance', 'income', 'other', NOW() - INTERVAL '15 days', 5, NOW(), NOW()),

-- Expenses
(500.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '22 days', 5, NOW(), NOW()),
(200.00, 'Roupas', 'expense', 'clothing', NOW() - INTERVAL '18 days', 5, NOW(), NOW()),
(250.00, 'Academia', 'expense', 'healthcare', NOW() - INTERVAL '15 days', 5, NOW(), NOW()),
(150.00, 'Livros', 'expense', 'education', NOW() - INTERVAL '10 days', 5, NOW(), NOW()),
(300.00, 'Presente Aniversário', 'expense', 'gifts', NOW() - INTERVAL '5 days', 5, NOW(), NOW()),
(250.00, 'Jantar fora', 'expense', 'entertainment', NOW() - INTERVAL '2 days', 5, NOW(), NOW());

-- Julia Santos (Daughter)
INSERT INTO transactions (amount, description, type, category, date, user_id, created_at, updated_at)
VALUES
-- Income
(1000.00, 'Mesada', 'income', 'other', NOW  date, user_id, created_at, updated_at)
VALUES
-- Income
(1000.00, 'Mesada', 'income', 'other', NOW() - INTERVAL '1 month', 6, NOW(), NOW()),
(1000.00, 'Mesada', 'income', 'other', NOW(), 6, NOW(), NOW()),
(300.00, 'Trabalho temporário', 'income', 'other', NOW() - INTERVAL '15 days', 6, NOW(), NOW()),

-- Expenses
(400.00, 'Material escolar', 'expense', 'education', NOW() - INTERVAL '25 days', 6, NOW(), NOW()),
(200.00, 'Lanche na escola', 'expense', 'food', NOW() - INTERVAL '20 days', 6, NOW(), NOW()),
(300.00, 'Jogos', 'expense', 'entertainment', NOW() - INTERVAL '15 days', 6, NOW(), NOW()),
(150.00, 'Roupas', 'expense', 'clothing', NOW() - INTERVAL '10 days', 6, NOW(), NOW()),
(80.00, 'Cinema', 'expense', 'entertainment', NOW() - INTERVAL '5 days', 6, NOW(), NOW());

-- Insert historical data for trend analysis (Family 1 - João Silva)
-- Last 6 months
INSERT INTO transactions (amount, description, type, category, date, user_id, created_at, updated_at)
VALUES
-- 6 months ago
(5000.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '6 months', 1, NOW() - INTERVAL '6 months', NOW() - INTERVAL '6 months'),
(1500.00, 'Aluguel', 'expense', 'housing', NOW() - INTERVAL '6 months', 1, NOW() - INTERVAL '6 months', NOW() - INTERVAL '6 months'),
(450.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '6 months', 1, NOW() - INTERVAL '6 months', NOW() - INTERVAL '6 months'),
(280.00, 'Conta de Luz', 'expense', 'utilities', NOW() - INTERVAL '6 months', 1, NOW() - INTERVAL '6 months', NOW() - INTERVAL '6 months'),
(200.00, 'Internet', 'expense', 'utilities', NOW() - INTERVAL '6 months', 1, NOW() - INTERVAL '6 months', NOW() - INTERVAL '6 months'),
(800.00, 'Parcela do Carro', 'expense', 'transportation', NOW() - INTERVAL '6 months', 1, NOW() - INTERVAL '6 months', NOW() - INTERVAL '6 months'),

-- 5 months ago
(5000.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '5 months', 1, NOW() - INTERVAL '5 months', NOW() - INTERVAL '5 months'),
(1500.00, 'Aluguel', 'expense', 'housing', NOW() - INTERVAL '5 months', 1, NOW() - INTERVAL '5 months', NOW() - INTERVAL '5 months'),
(480.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '5 months', 1, NOW() - INTERVAL '5 months', NOW() - INTERVAL '5 months'),
(290.00, 'Conta de Luz', 'expense', 'utilities', NOW() - INTERVAL '5 months', 1, NOW() - INTERVAL '5 months', NOW() - INTERVAL '5 months'),
(200.00, 'Internet', 'expense', 'utilities', NOW() - INTERVAL '5 months', 1, NOW() - INTERVAL '5 months', NOW() - INTERVAL '5 months'),
(800.00, 'Parcela do Carro', 'expense', 'transportation', NOW() - INTERVAL '5 months', 1, NOW() - INTERVAL '5 months', NOW() - INTERVAL '5 months'),

-- 4 months ago
(5000.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '4 months', 1, NOW() - INTERVAL '4 months', NOW() - INTERVAL '4 months'),
(1500.00, 'Aluguel', 'expense', 'housing', NOW() - INTERVAL '4 months', 1, NOW() - INTERVAL '4 months', NOW() - INTERVAL '4 months'),
(520.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '4 months', 1, NOW() - INTERVAL '4 months', NOW() - INTERVAL '4 months'),
(310.00, 'Conta de Luz', 'expense', 'utilities', NOW() - INTERVAL '4 months', 1, NOW() - INTERVAL '4 months', NOW() - INTERVAL '4 months'),
(200.00, 'Internet', 'expense', 'utilities', NOW() - INTERVAL '4 months', 1, NOW() - INTERVAL '4 months', NOW() - INTERVAL '4 months'),
(800.00, 'Parcela do Carro', 'expense', 'transportation', NOW() - INTERVAL '4 months', 1, NOW() - INTERVAL '4 months', NOW() - INTERVAL '4 months'),

-- 3 months ago
(5000.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '3 months', 1, NOW() - INTERVAL '3 months', NOW() - INTERVAL '3 months'),
(1500.00, 'Aluguel', 'expense', 'housing', NOW() - INTERVAL '3 months', 1, NOW() - INTERVAL '3 months', NOW() - INTERVAL '3 months'),
(490.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '3 months', 1, NOW() - INTERVAL '3 months', NOW() - INTERVAL '3 months'),
(300.00, 'Conta de Luz', 'expense', 'utilities', NOW() - INTERVAL '3 months', 1, NOW() - INTERVAL '3 months', NOW() - INTERVAL '3 months'),
(200.00, 'Internet', 'expense', 'utilities', NOW() - INTERVAL '3 months', 1, NOW() - INTERVAL '3 months', NOW() - INTERVAL '3 months'),
(800.00, 'Parcela do Carro', 'expense', 'transportation', NOW() - INTERVAL '3 months', 1, NOW() - INTERVAL '3 months', NOW() - INTERVAL '3 months'),

-- 2 months ago
(5000.00, 'Salário', 'income', 'salary', NOW() - INTERVAL '2 months', 1, NOW() - INTERVAL '2 months', NOW() - INTERVAL '2 months'),
(1500.00, 'Aluguel', 'expense', 'housing', NOW() - INTERVAL '2 months', 1, NOW() - INTERVAL '2 months', NOW() - INTERVAL '2 months'),
(510.00, 'Supermercado', 'expense', 'food', NOW() - INTERVAL '2 months', 1, NOW() - INTERVAL '2 months', NOW() - INTERVAL '2 months'),
(320.00, 'Conta de Luz', 'expense', 'utilities', NOW() - INTERVAL '2 months', 1, NOW() - INTERVAL '2 months', NOW() - INTERVAL '2 months'),
(200.00, 'Internet', 'expense', 'utilities', NOW() - INTERVAL '2 months', 1, NOW() - INTERVAL '2 months', NOW() - INTERVAL '2 months'),
(800.00, 'Parcela do Carro', 'expense', 'transportation', NOW() - INTERVAL '2 months', 1, NOW() - INTERVAL '2 months', NOW() - INTERVAL '2 months');

-- Insert goals
-- Family 1 Goals
INSERT INTO goals (title, description, target_amount, current_amount, deadline, is_completed, creator_id, created_at, updated_at)
VALUES
('Viagem para a Praia', 'Férias em família na praia no próximo verão', 5000.00, 2500.00, NOW() + INTERVAL '6 months', false, 1, NOW() - INTERVAL '3 months', NOW()),
('Novo Notebook', 'Comprar um notebook novo para o Pedro', 3000.00, 1500.00, NOW() + INTERVAL '2 months', false, 1, NOW() - INTERVAL '2 months', NOW()),
('Reforma da Casa', 'Pequena reforma na sala e cozinha', 10000.00, 3000.00, NOW() + INTERVAL '8 months', false, 2, NOW() - INTERVAL '4 months', NOW());

-- Family 2 Goals
INSERT INTO goals (title, description, target_amount, current_amount, deadline, is_completed, creator_id, created_at, updated_at)
VALUES
('Viagem para a Europa', 'Férias em família na Europa', 15000.00, 5000.00, NOW() + INTERVAL '12 months', false, 4, NOW() - INTERVAL '6 months', NOW()),
('Novo Carro', 'Trocar o carro da família', 30000.00, 10000.00, NOW() + INTERVAL '18 months', false, 4, NOW() - INTERVAL '8 months', NOW()),
('Curso de Inglês', 'Curso de inglês para a Julia', 2000.00, 1000.00, NOW() + INTERVAL '1 month', false, 5, NOW() - INTERVAL '3 months', NOW());

-- Add participants to goals
-- Family 1
INSERT INTO goal_participants (goal_id, user_id)
VALUES
(1, 1), (1, 2), (1, 3), -- All family members for beach trip
(2, 1), (2, 3), -- João and Pedro for notebook
(3, 1), (3, 2); -- João and Maria for house renovation

-- Family 2
INSERT INTO goal_participants (goal_id, user_id)
VALUES
(4, 4), (4, 5), (4, 6), -- All family members for Europe trip
(5, 4), (5, 5), -- Ana and Carlos for new car
(6, 4), (6, 6); -- Ana and Julia for English course

-- Add goal contributions
-- Family 1 - Beach Trip
INSERT INTO goal_contributions (amount, goal_id, user_id, date)
VALUES
(1000.00, 1, 1, NOW() - INTERVAL '3 months'), -- João
(800.00, 1, 2, NOW() - INTERVAL '2 months'), -- Maria
(500.00, 1, 1, NOW() - INTERVAL '1 month'), -- João
(200.00, 1, 3, NOW() - INTERVAL '15 days'); -- Pedro

-- Family 1 - Notebook
INSERT INTO goal_contributions (amount, goal_id, user_id, date)
VALUES
(1000.00, 2, 1, NOW() - INTERVAL '2 months'), -- João
(300.00, 2, 3, NOW() - INTERVAL '1 month'), -- Pedro
(200.00, 2, 3, NOW() - INTERVAL '15 days'); -- Pedro

-- Family 1 - House Renovation
INSERT INTO goal_contributions (amount, goal_id, user_id, date)
VALUES
(1500.00, 3, 1, NOW() - INTERVAL '4 months'), -- João
(1000.00, 3, 2, NOW() - INTERVAL '3 months'), -- Maria
(500.00, 3, 1, NOW() - INTERVAL '1 month'); -- João

-- Family 2 - Europe Trip
INSERT INTO goal_contributions (amount, goal_id, user_id, date)
VALUES
(2000.00, 4, 4, NOW() - INTERVAL '6 months'), -- Ana
(1500.00, 4, 5, NOW() - INTERVAL '4 months'), -- Carlos
(1000.00, 4, 4, NOW() - INTERVAL '2 months'), -- Ana
(500.00, 4, 6, NOW() - INTERVAL '1 month'); -- Julia

-- Family 2 - New Car
INSERT INTO goal_contributions (amount, goal_id, user_id, date)
VALUES
(5000.00, 5, 4, NOW() - INTERVAL '8 months'), -- Ana
(3000.00, 5, 5, NOW() - INTERVAL '6 months'), -- Carlos
(2000.00, 5, 4, NOW() - INTERVAL '3 months'); -- Ana

-- Family 2 - English Course
INSERT INTO goal_contributions (amount, goal_id, user_id, date)
VALUES
(500.00, 6, 4, NOW() - INTERVAL '3 months'), -- Ana
(300.00, 6, 6, NOW() - INTERVAL '2 months'), -- Julia
(200.00, 6, 6, NOW() - INTERVAL '1 month'); -- Julia

-- Insert notifications
-- Family 1
INSERT INTO notifications (title, message, type, is_read, user_id, created_at)
VALUES
-- João Silva
('Alerta de Orçamento', 'Você já utilizou 75% do seu orçamento mensal.', 'budget_warning', false, 1, NOW() - INTERVAL '10 days'),
('Nova Meta Adicionada', 'Você foi adicionado à meta "Viagem para a Praia"', 'goal_contribution', true, 1, NOW() - INTERVAL '3 months'),
('Nova Contribuição para Meta', 'Maria contribuiu R$800.00 para a meta "Viagem para a Praia".', 'goal_contribution', true, 1, NOW() - INTERVAL '2 months'),

-- Maria Silva
('Alerta de Orçamento', 'Você já utilizou 70% do seu orçamento mensal.', 'budget_warning', true, 2, NOW() - INTERVAL '12 days'),
('Nova Meta Adicionada', 'Você foi adicionado à meta "Viagem para a Praia"', 'goal_contribution', true, 2, NOW() - INTERVAL '3 months'),
('Nova Contribuição para Meta', 'João contribuiu R$1000.00 para a meta "Viagem para a Praia".', 'goal_contribution', true, 2, NOW() - INTERVAL '3 months'),

-- Pedro Silva
('Nova Meta Adicionada', 'Você foi adicionado à meta "Viagem para a Praia"', 'goal_contribution', true, 3, NOW() - INTERVAL '3 months'),
('Nova Meta Adicionada', 'Você foi adicionado à meta "Novo Notebook"', 'goal_contribution', true, 3, NOW() - INTERVAL '2 months'),
('Nova Contribuição para Meta', 'João contribuiu R$1000.00 para a meta "Novo Notebook".', 'goal_contribution', true, 3, NOW() - INTERVAL '2 months');

-- Family 2
INSERT INTO notifications (title, message, type, is_read, user_id, created_at)
VALUES
-- Ana Santos
('Alerta Crítico de Orçamento', 'Crítico: Você já utilizou 90% do seu orçamento mensal!', 'budget_critical', false, 4, NOW() - INTERVAL '5 days'),
('Nova Meta Adicionada', 'Você foi adicionado à meta "Viagem para a Europa"', 'goal_contribution', true, 4, NOW() - INTERVAL '6 months'),
('Nova Contribuição para Meta', 'Carlos contribuiu R$1500.00 para a meta "Viagem para a Europa".', 'goal_contribution', true, 4, NOW() - INTERVAL '4 months'),

-- Carlos Santos
('Alerta de Orçamento', 'Você já utilizou 75% do seu orçamento mensal.', 'budget_warning', true, 5, NOW() - INTERVAL '8 days'),
('Nova Meta Adicionada', 'Você foi adicionado à meta "Viagem para a Europa"', 'goal_contribution', true, 5, NOW() - INTERVAL '6 months'),
('Nova Contribuição para Meta', 'Ana contribuiu R$2000.00 para a meta "Viagem para a Europa".', 'goal_contribution', true, 5, NOW() - INTERVAL '6 months'),

-- Julia Santos
('Nova Meta Adicionada', 'Você foi adicionado à meta "Viagem para a Europa"', 'goal_contribution', true, 6, NOW() - INTERVAL '6 months'),
('Nova Meta Adicionada', 'Você foi adicionado à meta "Curso de Inglês"', 'goal_contribution', true, 6, NOW() - INTERVAL '3 months'),
('Nova Contribuição para Meta', 'Ana contribuiu R$500.00 para a meta "Curso de Inglês".', 'goal_contribution', true, 6, NOW() - INTERVAL '3 months');
