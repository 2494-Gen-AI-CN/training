-- The five objects the library gets on Friday. The tests pipe this file into
-- docker exec -i desk-mysql mysql -uroot -pdesk library_routines_test
-- after the tables and rows exist, so the file needs no USE line.
-- Write each trigger and procedure body between DELIMITER // and DELIMITER ;
-- and end it with END //

-- trigger loans_returned: AFTER UPDATE ON loans; when returned_on goes from NULL
-- to a date, insert a loan_events row (loan_id, kind 'returned')

-- view overdue_loans: loan_id, member (members.name), title, due_on for the loans
-- with returned_on NULL and due_on before CURDATE(), ordered by due_on then loan_id

-- procedure close_loan(IN p_loan_id INT, IN p_returned_on DATE): sets returned_on
-- on the loan only if it has not been returned yet

-- function late_fee(p_due DATE, p_returned DATE) RETURNS DECIMAL(6,2), DETERMINISTIC:
-- 0.25 for each day returned after due, 0.00 when on time or early

-- index idx_loans_due_on on loans (due_on)
