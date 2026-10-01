USE skillpath_ai;

DELETE FROM career_skills;
DELETE FROM earnings;
DELETE FROM jobs;
DELETE FROM careers;
DELETE FROM training_centres;

INSERT INTO careers
(career_name,sector,description,education_required,training_duration,nsqf_level)
VALUES
('Automobile Technician','Automotive',
'Diagnoses, services and repairs conventional and modern vehicles.',
'Class 10 / ITI pathway','1-2 years','Level 4'),
('Electrician','Electrical',
'Installs, maintains and repairs electrical systems and equipment.',
'Class 10 / ITI pathway','1-2 years','Level 4'),
('EV Technician','Automotive & EV',
'Works on electric vehicle systems, diagnostics, batteries and safety procedures.',
'Class 10 / ITI or EV course','1-2 years','Level 4-5'),
('Solar Technician','Renewable Energy',
'Installs, tests and maintains solar photovoltaic systems.',
'Class 10 / ITI pathway','6-18 months','Level 4'),
('Electronics Technician','Electronics',
'Tests, repairs and maintains electronic equipment and devices.',
'Class 10 / ITI pathway','1-2 years','Level 4'),
('CNC Operator','Manufacturing',
'Operates computer-controlled machines used in precision manufacturing.',
'Class 10 / ITI pathway','1-2 years','Level 4'),
('Welder','Manufacturing',
'Joins and repairs metal components using appropriate welding processes.',
'Class 10 / ITI pathway','6-12 months','Level 3-4'),
('Healthcare Assistant','Healthcare',
'Supports basic patient-care and healthcare service activities.',
'Class 10/12 depending on pathway','6-18 months','Level 3-4');

INSERT INTO career_skills(career_id,skill_name,importance)
SELECT id,'hands-on',5 FROM careers WHERE career_name='Automobile Technician'
UNION ALL SELECT id,'technical',5 FROM careers WHERE career_name='Automobile Technician'
UNION ALL SELECT id,'problem solving',4 FROM careers WHERE career_name='Automobile Technician'
UNION ALL SELECT id,'technical',5 FROM careers WHERE career_name='Electrician'
UNION ALL SELECT id,'hands-on',5 FROM careers WHERE career_name='Electrician'
UNION ALL SELECT id,'problem solving',4 FROM careers WHERE career_name='Electrician'
UNION ALL SELECT id,'technical',5 FROM careers WHERE career_name='EV Technician'
UNION ALL SELECT id,'digital',4 FROM careers WHERE career_name='EV Technician'
UNION ALL SELECT id,'problem solving',5 FROM careers WHERE career_name='EV Technician'
UNION ALL SELECT id,'technical',5 FROM careers WHERE career_name='Solar Technician'
UNION ALL SELECT id,'hands-on',5 FROM careers WHERE career_name='Solar Technician'
UNION ALL SELECT id,'problem solving',4 FROM careers WHERE career_name='Solar Technician'
UNION ALL SELECT id,'technical',5 FROM careers WHERE career_name='Electronics Technician'
UNION ALL SELECT id,'digital',4 FROM careers WHERE career_name='Electronics Technician'
UNION ALL SELECT id,'problem solving',4 FROM careers WHERE career_name='Electronics Technician'
UNION ALL SELECT id,'technical',5 FROM careers WHERE career_name='CNC Operator'
UNION ALL SELECT id,'hands-on',5 FROM careers WHERE career_name='CNC Operator'
UNION ALL SELECT id,'problem solving',4 FROM careers WHERE career_name='CNC Operator'
UNION ALL SELECT id,'hands-on',5 FROM careers WHERE career_name='Welder'
UNION ALL SELECT id,'technical',4 FROM careers WHERE career_name='Welder'
UNION ALL SELECT id,'communication',5 FROM careers WHERE career_name='Healthcare Assistant'
UNION ALL SELECT id,'problem solving',4 FROM careers WHERE career_name='Healthcare Assistant';

INSERT INTO jobs(career_id,company_name,job_title,location,minimum_salary,maximum_salary,experience_required)
SELECT id,'Demo Auto Services','Automobile Technician','Delhi NCR',14000,26000,'0-2 years' FROM careers WHERE career_name='Automobile Technician'
UNION ALL SELECT id,'Demo Motors','Service Technician','Lucknow',15000,28000,'0-2 years' FROM careers WHERE career_name='Automobile Technician'
UNION ALL SELECT id,'Demo EV Mobility','EV Service Technician','Delhi NCR',18000,32000,'0-2 years' FROM careers WHERE career_name='EV Technician'
UNION ALL SELECT id,'Demo Energy','Solar Technician','Jaipur',16000,30000,'0-2 years' FROM careers WHERE career_name='Solar Technician'
UNION ALL SELECT id,'Demo Power Solutions','Electrician','Meerut',14000,27000,'0-2 years' FROM careers WHERE career_name='Electrician'
UNION ALL SELECT id,'Demo Electronics','Electronics Technician','Noida',16000,29000,'0-2 years' FROM careers WHERE career_name='Electronics Technician'
UNION ALL SELECT id,'Demo Manufacturing','CNC Operator','Gurugram',18000,33000,'0-2 years' FROM careers WHERE career_name='CNC Operator'
UNION ALL SELECT id,'Demo Fabrication','Welder','Faridabad',15000,28000,'0-2 years' FROM careers WHERE career_name='Welder'
UNION ALL SELECT id,'Demo Healthcare','Healthcare Assistant','Delhi NCR',14000,25000,'0-2 years' FROM careers WHERE career_name='Healthcare Assistant';

INSERT INTO earnings(career_id,experience_years,minimum_salary,maximum_salary)
SELECT id,0,12000,18000 FROM careers
UNION ALL SELECT id,2,16000,26000 FROM careers
UNION ALL SELECT id,5,24000,40000 FROM careers
UNION ALL SELECT id,8,32000,55000 FROM careers;

INSERT INTO training_centres(centre_name,location,course_name,duration,contact)
VALUES
('Demo Skill Training Centre - Delhi','Delhi','Automobile Technician','2 years','011-00000000'),
('Demo Skill Training Centre - Meerut','Meerut','Electrician','2 years','0121-0000000'),
('Demo EV Training Hub','Noida','EV Technician','1 year','0120-0000000'),
('Demo Renewable Skills Centre','Jaipur','Solar Technician','1 year','0141-0000000'),
('Demo Electronics Skill Centre','Gurugram','Electronics Technician','2 years','0124-0000000');
