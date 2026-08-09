-- Seed Trivia Questions
-- These are example questions. Add more as needed!

INSERT INTO trivia_questions (guild_id, category, difficulty, question, correct_answer, incorrect_answers) VALUES

-- General Knowledge - Easy
(NULL, 'General', 'easy', 'What is the capital of France?', 'Paris', ARRAY['London', 'Berlin', 'Madrid']),
(NULL, 'General', 'easy', 'How many continents are there?', 'Seven', ARRAY['Five', 'Six', 'Eight']),
(NULL, 'General', 'easy', 'What is the largest ocean on Earth?', 'Pacific Ocean', ARRAY['Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean']),
(NULL, 'General', 'easy', 'What is 2 + 2?', '4', ARRAY['3', '5', '22']),

-- Science - Easy
(NULL, 'Science', 'easy', 'What planet is known as the Red Planet?', 'Mars', ARRAY['Venus', 'Jupiter', 'Saturn']),
(NULL, 'Science', 'easy', 'What gas do plants absorb from the atmosphere?', 'Carbon Dioxide', ARRAY['Oxygen', 'Nitrogen', 'Hydrogen']),
(NULL, 'Science', 'easy', 'How many bones are in the human body?', '206', ARRAY['195', '210', '186']),

-- Gaming - Easy
(NULL, 'Gaming', 'easy', 'What game features a character named Mario?', 'Super Mario Bros', ARRAY['Sonic', 'Zelda', 'Pokemon']),
(NULL, 'Gaming', 'easy', 'What color is Sonic the Hedgehog?', 'Blue', ARRAY['Red', 'Green', 'Yellow']),
(NULL, 'Gaming', 'easy', 'In Minecraft, what do you mine for diamonds?', 'Pickaxe', ARRAY['Shovel', 'Axe', 'Sword']),

-- Movies - Easy
(NULL, 'Movies', 'easy', 'Who directed the movie "Jurassic Park"?', 'Steven Spielberg', ARRAY['James Cameron', 'George Lucas', 'Christopher Nolan']),
(NULL, 'Movies', 'easy', 'What year was the first "Toy Story" movie released?', '1995', ARRAY['1990', '2000', '1998']),

-- General Knowledge - Medium
(NULL, 'General', 'medium', 'What is the smallest country in the world?', 'Vatican City', ARRAY['Monaco', 'San Marino', 'Liechtenstein']),
(NULL, 'General', 'medium', 'Who painted the Mona Lisa?', 'Leonardo da Vinci', ARRAY['Michelangelo', 'Raphael', 'Donatello']),
(NULL, 'General', 'medium', 'What is the chemical symbol for gold?', 'Au', ARRAY['Go', 'Gd', 'Ag']),

-- Science - Medium
(NULL, 'Science', 'medium', 'What is the speed of light?', '299,792,458 m/s', ARRAY['300,000,000 m/s', '186,000 mph', '250,000,000 m/s']),
(NULL, 'Science', 'medium', 'What is the powerhouse of the cell?', 'Mitochondria', ARRAY['Nucleus', 'Ribosome', 'Chloroplast']),

-- Gaming - Medium
(NULL, 'Gaming', 'medium', 'What year was the first PlayStation released?', '1994', ARRAY['1996', '1992', '1998']),
(NULL, 'Gaming', 'medium', 'Who is the main protagonist in "The Legend of Zelda" series?', 'Link', ARRAY['Zelda', 'Ganon', 'Epona']),

-- General Knowledge - Hard
(NULL, 'General', 'hard', 'What is the most spoken language in the world by native speakers?', 'Mandarin Chinese', ARRAY['English', 'Spanish', 'Hindi']),
(NULL, 'General', 'hard', 'Who wrote "The Divine Comedy"?', 'Dante Alighieri', ARRAY['Virgil', 'Homer', 'Ovid']),

-- Science - Hard
(NULL, 'Science', 'hard', 'What is the name of the largest known star?', 'UY Scuti', ARRAY['Betelgeuse', 'VY Canis Majoris', 'Antares']),
(NULL, 'Science', 'hard', 'What is the Heisenberg Uncertainty Principle?', 'Cannot simultaneously know position and momentum', ARRAY['Energy cannot be created or destroyed', 'Every action has a reaction', 'Mass equals energy'])

ON CONFLICT DO NOTHING;
