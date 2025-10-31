-- \connect pkm_db

-- -- main topics
-- -- INSERT INTO main_app_category (name, parent_id, color, hierarchy) VALUES 
-- -- ('Technical Mastery', null, '#1f77b4', 1),
-- -- ('Soft & Interpersonal Skills', null, '#ff7f0e', 1),
-- -- ('Personal & Habitual Skills', null, '#2ca02c', 1);

-- -- -- technical skills
-- INSERT INTO main_app_category (name, parent_id, color, hierarchy) VALUES
-- ('Core Programming & CS Fundamentals', 57, '#aec7e8', 2),
-- ('Frontend Development', 57, '#1f77b4', 2),
-- ('Backend Development', 57, '#17becf', 2),
-- ('Software Design & Architecture', 57, '#c7c7c7', 2),
-- ('Cloud, DevOps & Infrastructure', 57, '#9467bd', 2),
-- ('Testing & Quality Assurance', 57, '#8c564b', 2),
-- ('Databases & Data Management', 57, '#e377c2', 2),
-- ('AI / Machine Learning & Data Skills', 57, '#7f7f7f', 2),
-- ('Security & Cybersecurity Awareness', 57, '#bcbd22', 2),
-- ('System Design & Scalability', 57, '#ffbb78', 2),
-- ('Software Engineering Practices', 57, '#d62728', 2),

-- -- -- soft skills
-- ('Communication Skills', 58, '#ff9896', 2),
-- ('Collaboration & Teamwork', 58, '#c49c94', 2),
-- ('Problem Solving & Critical Thinking', 58, '#f7b6d2', 2),
-- ('Leadership', 58, '#dbdb8d', 2),
-- ('Time & Task Management', 58, '#9edae5', 2),

-- -- -- personal & habitual skills
-- ('Deep Work & Focus', 59, '#17becf', 2),
-- ('Discipline & Consistency', 59, '#bcbd22', 2),
-- ('Professionalism & Work Ethics', 59, '#ff9896', 2),
-- ('Documentation & Knowledge Management', 59, '#c5b0d5', 2),
-- ('Self-Reflection & Improvement', 59, '#ff7f0e', 2),
-- ('Mental & Physical Well-being', 59, '#2ca02c', 2),
-- ('Curiosity & Continuous Learning', 59, '#8c564b', 2);

INSERT INTO main_app_category (name, parent_id, color, hierarchy)
VALUES ('Data Structures Mastery', 63, '#ffbb78', 3);

INSERT INTO main_app_category (name, parent_id, color, hierarchy)
VALUES ('Algorithms & Problem Solving', 63, '#98df8a', 3);

INSERT INTO main_app_category (name, parent_id, color, hierarchy)
VALUES ('Time & Space Complexity (Big-O)', 63, '#c5b0d5', 3);

-- INSERT INTO main_app_category (name, parent_id, color, hierarchy)
-- VALUES ('HTML & Semantic Structure', 64, '#aec7e8', 3);

-- INSERT INTO main_app_category (name, parent_id, color, hierarchy)
-- VALUES ('CSS Positioning & Layout (Flexbox/Grid)', 64, '#1f77b4', 3);

-- INSERT INTO main_app_category (name, parent_id, color, hierarchy)
-- VALUES ('JavaScript Foundations', 64, '#ff7f0e', 3);

-- INSERT INTO main_app_category (name, parent_id, color, hierarchy)
-- VALUES ('React Basics (Components, Props, State)', 64, '#2ca02c', 3);

