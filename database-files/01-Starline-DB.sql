DROP DATABASE IF EXISTS `Starline-DB`;
CREATE DATABASE `Starline-DB`;
USE `Starline-DB`;

CREATE TABLE users (
  user_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  class_year INT,
  housing_type VARCHAR(50),

  PRIMARY KEY (user_id),
  UNIQUE INDEX uq_idx_users_email (email)
);


CREATE TABLE categories (
  category_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'active',

  PRIMARY KEY (category_id)
);


CREATE TABLE club_budgets (
  budget_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  semester VARCHAR(50),
  managed_by_user_id INT,

  PRIMARY KEY (budget_id),
  INDEX idx_club_budgets_managed_by_user_id (managed_by_user_id),

  CONSTRAINT fk_club_budgets_users
    FOREIGN KEY (managed_by_user_id) REFERENCES users(user_id)
);


CREATE TABLE events (
  event_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  date DATE NOT NULL,
  managed_by_budget_id INT,

  PRIMARY KEY (event_id),
  INDEX idx_events_managed_by_budget_id (managed_by_budget_id),

  CONSTRAINT fk_events_club_budgets
    FOREIGN KEY (managed_by_budget_id) REFERENCES club_budgets(budget_id)
);


CREATE TABLE budget_templates (
  template_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  status VARCHAR(50)  NOT NULL DEFAULT 'draft',
  managed_by_user_id INT,
  category_id INT,

  PRIMARY KEY (template_id),
  INDEX idx_budget_templates_managed_by_user_id (managed_by_user_id),
  INDEX idx_budget_templates_category_id (category_id),

  CONSTRAINT fk_budget_templates_users
    FOREIGN KEY (managed_by_user_id) REFERENCES users(user_id),
  CONSTRAINT fk_budget_templates_categories
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);


CREATE TABLE system_settings (
  setting_id INT NOT NULL AUTO_INCREMENT,
  alert_threshold DECIMAL(10,2),
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  updated_by_user_id INT,

  PRIMARY KEY (setting_id),
  INDEX idx_system_settings_updated_by_user_id (updated_by_user_id),

  CONSTRAINT fk_system_settings_users
    FOREIGN KEY (updated_by_user_id) REFERENCES users(user_id)
);


CREATE TABLE support_issues (
  issue_id INT NOT NULL AUTO_INCREMENT,
  description TEXT,
  status VARCHAR(50) NOT NULL DEFAULT 'open',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  submitted_by_user_id INT,

  PRIMARY KEY (issue_id),
  INDEX idx_support_issues_submitted_by_user_id (submitted_by_user_id),

  CONSTRAINT fk_support_issues_users
    FOREIGN KEY (submitted_by_user_id) REFERENCES users(user_id)
);


CREATE TABLE dashboard_filters (
  filter_id INT NOT NULL AUTO_INCREMENT,
  filter_type VARCHAR(50) NOT NULL,
  value VARCHAR(100),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  user_id INT,

  PRIMARY KEY (filter_id),
  INDEX idx_dashboard_filters_user_id (user_id),

  CONSTRAINT fk_dashboard_filters_users
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE TABLE budget_goals (
  goal_id INT NOT NULL AUTO_INCREMENT,
  target_amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'active',
  semester VARCHAR(50),
  budget_id  INT NOT NULL,
  set_by_user_id INT,
  event_id INT,                   

  PRIMARY KEY (goal_id),
  INDEX idx_budget_goals_set_by_user_id (set_by_user_id),
  INDEX idx_budget_goals_budget_id (budget_id),
  INDEX idx_budget_goals_event_id (event_id),

  CONSTRAINT fk_budget_goals_users
    FOREIGN KEY (set_by_user_id) REFERENCES users(user_id),
  CONSTRAINT fk_budget_goals_events
    FOREIGN KEY (event_id) REFERENCES events(event_id),
  CONSTRAINT fk_budget_goals_club_budgets
    FOREIGN KEY (budget_id) REFERENCES club_budgets(budget_id)
);


CREATE TABLE shared_expenses (
  expense_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  date DATE NOT NULL,
  paid_by_user_id INT NOT NULL,
  category_id INT,

  PRIMARY KEY (expense_id),
  INDEX idx_shared_expenses_paid_by_user_id (paid_by_user_id),
  INDEX idx_shared_expenses_category_id (category_id),

  CONSTRAINT fk_shared_expenses_users
    FOREIGN KEY (paid_by_user_id) REFERENCES users(user_id),
  CONSTRAINT fk_shared_expenses_categories
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);


CREATE TABLE expense_splits (
  split_id INT NOT NULL AUTO_INCREMENT, 
  expense_id INT NOT NULL,
  user_id INT NOT NULL,
  amount_owed DECIMAL(10,2) NOT NULL,
  is_paid TINYINT(1) NOT NULL DEFAULT 0,

  PRIMARY KEY (split_id),
  UNIQUE INDEX uq_expense_splits_expense_user (expense_id, user_id), 
  INDEX idx_expense_splits_user_id (user_id),

  CONSTRAINT fk_expense_splits_shared_expenses
    FOREIGN KEY (expense_id) REFERENCES shared_expenses(expense_id),
  CONSTRAINT fk_expense_splits_users
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE TABLE club_expenses (
  expense_id INT NOT NULL AUTO_INCREMENT,
  description TEXT,
  amount DECIMAL(10,2) NOT NULL,
  date DATE NOT NULL,
  receipt_url VARCHAR(255),
  notes TEXT,
  needs_reimbursement TINYINT(1) NOT NULL DEFAULT 0,
  paid_by_user_id INT NOT NULL,
  budget_id INT NOT NULL,
  category_id INT,
  event_id INT,
  goal_id INT,

  PRIMARY KEY (expense_id),
  INDEX idx_club_expenses_paid_by_user_id (paid_by_user_id),
  INDEX idx_club_expenses_budget_id (budget_id),
  INDEX idx_club_expenses_category_id (category_id),
  INDEX idx_club_expenses_event_id (event_id),
  INDEX idx_club_expenses_goal_id (goal_id),

  CONSTRAINT fk_club_expenses_users
    FOREIGN KEY (paid_by_user_id) REFERENCES users(user_id),
  CONSTRAINT fk_club_expenses_club_budgets
    FOREIGN KEY (budget_id) REFERENCES club_budgets(budget_id),
  CONSTRAINT fk_club_expenses_categories
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
  CONSTRAINT fk_club_expenses_events
    FOREIGN KEY (event_id) REFERENCES events(event_id),
  CONSTRAINT fk_club_expenses_budget_goals
    FOREIGN KEY (goal_id) REFERENCES budget_goals(goal_id)
);


CREATE TABLE reimbursements (
  reimb_id INT NOT NULL AUTO_INCREMENT,  
  expense_id INT NOT NULL,
  user_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  is_paid TINYINT(1) NOT NULL DEFAULT 0,

  PRIMARY KEY (reimb_id),
  UNIQUE INDEX uq_reimbursements_expense_user (expense_id, user_id),  
  INDEX idx_reimbursements_user_id (user_id),

  CONSTRAINT fk_reimbursements_club_expenses
    FOREIGN KEY (expense_id) REFERENCES club_expenses(expense_id),
  CONSTRAINT fk_reimbursements_users
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE TABLE flagged_transactions (
  flag_id INT NOT NULL AUTO_INCREMENT,
  shared_expense_id INT NULL,  
  club_expense_id INT NULL,  
  flag_reason TEXT,
  status VARCHAR(50) NOT NULL DEFAULT 'open',
  reviewed_by_user_id INT,

  PRIMARY KEY (flag_id),
  INDEX idx_flagged_transactions_shared_expense_id (shared_expense_id),
  INDEX idx_flagged_transactions_club_expense_id (club_expense_id),
  INDEX idx_flagged_transactions_reviewed_by_user_id (reviewed_by_user_id),

  CONSTRAINT chk_flagged_transactions_one_target CHECK (
    (shared_expense_id IS NOT NULL AND club_expense_id IS NULL) OR
    (shared_expense_id IS NULL AND club_expense_id IS NOT NULL)
  ),

  CONSTRAINT fk_flagged_transactions_shared_expenses
    FOREIGN KEY (shared_expense_id) REFERENCES shared_expenses(expense_id),
  CONSTRAINT fk_flagged_transactions_club_expenses
    FOREIGN KEY (club_expense_id) REFERENCES club_expenses(expense_id),
  CONSTRAINT fk_flagged_transactions_users
    FOREIGN KEY (reviewed_by_user_id) REFERENCES users(user_id)
);