
from app import create_app
from models import db, Course, Module, Quiz, QuizQuestion, Assignment

def populate_courses():
    from flask import current_app
    
    if current_app:
        ctx = None
    else:
        app = create_app()
        ctx = app.app_context()
        ctx.push()
    
    try:
        if Course.query.count() > 0:
            print("Courses already exist. Skipping population.")
            return
        
        courses_data = [
            {
                'title': 'Cyber Security Fundamentals',
                'description': 'Master cybersecurity from basics to advanced techniques. Learn network security, ethical hacking, cryptography, and security best practices.',
                'price_ngn': 45000,
                'price_usd': 30,
                'image_url': 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400',
                'modules': [
                    {
                        'title': 'Introduction to Cybersecurity',
                        'content': 'Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. In this module, you will learn about the CIA triad (Confidentiality, Integrity, Availability), common cyber threats like malware, phishing, ransomware, and DDoS attacks. We will explore the cybersecurity landscape, understand the importance of security in our digital age, and examine real-world case studies of major security breaches.',
                        'video_url': 'https://www.youtube.com/embed/inWWhr5tnEA',
                        'quiz': {
                            'title': 'Cybersecurity Basics Quiz',
                            'questions': [
                                {
                                    'question': 'What does the CIA triad stand for in cybersecurity?',
                                    'option_a': 'Confidentiality, Integrity, Availability',
                                    'option_b': 'Central Intelligence Agency',
                                    'option_c': 'Cyber Intelligence Analysis',
                                    'option_d': 'Computer Information Access',
                                    'correct_answer': 'A'
                                },
                                {
                                    'question': 'Which of the following is a social engineering attack?',
                                    'option_a': 'DDoS Attack',
                                    'option_b': 'Phishing',
                                    'option_c': 'SQL Injection',
                                    'option_d': 'Buffer Overflow',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'What is the primary purpose of encryption?',
                                    'option_a': 'To speed up data transmission',
                                    'option_b': 'To protect data confidentiality',
                                    'option_c': 'To compress files',
                                    'option_d': 'To delete viruses',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Network Security Fundamentals',
                        'content': 'Network security involves protecting network infrastructure from unauthorized access, misuse, and threats. Learn about firewalls, VPNs, IDS/IPS systems, network segmentation, and secure network architecture. We will cover the OSI model, TCP/IP protocols, common network attacks (man-in-the-middle, ARP spoofing, DNS poisoning), and how to implement network security controls using tools like Wireshark for packet analysis.',
                        'video_url': 'https://www.youtube.com/embed/qiQR5rTSshw',
                        'quiz': {
                            'title': 'Network Security Quiz',
                            'questions': [
                                {
                                    'question': 'What does a firewall primarily do?',
                                    'option_a': 'Filters network traffic based on rules',
                                    'option_b': 'Encrypts all data',
                                    'option_c': 'Speeds up internet connection',
                                    'option_d': 'Removes viruses',
                                    'correct_answer': 'A'
                                },
                                {
                                    'question': 'Which protocol is used for secure web browsing?',
                                    'option_a': 'HTTP',
                                    'option_b': 'FTP',
                                    'option_c': 'HTTPS',
                                    'option_d': 'SMTP',
                                    'correct_answer': 'C'
                                }
                            ]
                        },
                        'assignment': {
                            'title': 'Network Security Assessment',
                            'description': 'Analyze the provided network diagram and identify at least 5 security vulnerabilities. For each vulnerability, explain the risk and propose a mitigation strategy. Consider aspects like firewall placement, network segmentation, VPN implementation, and access controls.'
                        }
                    },
                    {
                        'title': 'Ethical Hacking & Penetration Testing',
                        'content': 'Ethical hacking involves authorized testing of systems to find vulnerabilities before malicious hackers do. Learn the five phases of penetration testing: reconnaissance, scanning, gaining access, maintaining access, and covering tracks. We will explore tools like Nmap, Metasploit, Burp Suite, and Kali Linux. Understand OWASP Top 10 vulnerabilities, SQL injection, XSS attacks, and how to write comprehensive penetration testing reports.',
                        'video_url': 'https://www.youtube.com/embed/3Kq1MIfTWCE',
                        'assignment': {
                            'title': 'Penetration Testing Report',
                            'description': 'Using a provided vulnerable web application (or a lab environment), conduct a penetration test and write a professional report. Include executive summary, methodology, findings with severity ratings, proof of concept, and remediation recommendations.'
                        }
                    },
                    {
                        'title': 'Cryptography Essentials',
                        'content': 'Cryptography is the science of securing information through encoding. Learn about symmetric encryption (AES, DES), asymmetric encryption (RSA, ECC), hashing algorithms (SHA-256, MD5), digital signatures, and PKI (Public Key Infrastructure). Understand how SSL/TLS works, key exchange protocols, and practical applications of cryptography in securing communications.',
                        'video_url': 'https://www.youtube.com/embed/jhXCTbFnK8o',
                        'quiz': {
                            'title': 'Cryptography Quiz',
                            'questions': [
                                {
                                    'question': 'What is the main difference between symmetric and asymmetric encryption?',
                                    'option_a': 'Speed of encryption',
                                    'option_b': 'Number of keys used',
                                    'option_c': 'Type of algorithm',
                                    'option_d': 'Length of encrypted data',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which is NOT a hashing algorithm?',
                                    'option_a': 'SHA-256',
                                    'option_b': 'MD5',
                                    'option_c': 'AES',
                                    'option_d': 'bcrypt',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    }
                ]
            },
            {
                'title': 'Graphics Design Masterclass',
                'description': 'From beginner to professional designer. Master Adobe Creative Suite, design theory, branding, and create stunning visual content for digital and print media.',
                'price_ngn': 35000,
                'price_usd': 25,
                'image_url': 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=400',
                'modules': [
                    {
                        'title': 'Design Theory & Principles',
                        'content': 'Design is more than making things look pretty - it is about effective visual communication. Learn the fundamental principles: balance, contrast, emphasis, movement, pattern, rhythm, and unity. Master color theory including the color wheel, complementary colors, analogous colors, and color psychology. Understand typography fundamentals: serif vs sans-serif, font pairing, hierarchy, kerning, and leading. Study composition techniques like the rule of thirds, golden ratio, and visual hierarchy.',
                        'video_url': 'https://www.youtube.com/embed/YqQx75OPRa0',
                        'quiz': {
                            'title': 'Design Principles Quiz',
                            'questions': [
                                {
                                    'question': 'What are the three primary colors in traditional color theory?',
                                    'option_a': 'Red, Yellow, Blue',
                                    'option_b': 'Red, Green, Blue',
                                    'option_c': 'Cyan, Magenta, Yellow',
                                    'option_d': 'Orange, Purple, Green',
                                    'correct_answer': 'A'
                                },
                                {
                                    'question': 'Which design principle creates visual interest through differences?',
                                    'option_a': 'Balance',
                                    'option_b': 'Contrast',
                                    'option_c': 'Unity',
                                    'option_d': 'Pattern',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'What does kerning refer to in typography?',
                                    'option_a': 'Space between lines',
                                    'option_b': 'Font size',
                                    'option_c': 'Space between individual characters',
                                    'option_d': 'Font weight',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Adobe Photoshop Mastery',
                        'content': 'Photoshop is the industry standard for image editing and manipulation. Master the interface, layers, masks, adjustment layers, and blending modes. Learn advanced techniques: photo retouching, compositing, color grading, frequency separation, dodge and burn. Explore filters, smart objects, and non-destructive editing workflows. Create stunning social media graphics, posters, and photo manipulations. Understand resolution, file formats (JPEG, PNG, TIFF, PSD), and optimizing images for web and print.',
                        'video_url': 'https://www.youtube.com/embed/IyR_uYsRdPs',
                        'assignment': {
                            'title': 'Photo Manipulation Project',
                            'description': 'Create a surreal photo manipulation combining at least 4 different images. Apply advanced techniques including masking, color matching, lighting adjustments, and shadows. Submit your final PSD file with organized layers and a JPEG export.'
                        }
                    },
                    {
                        'title': 'Adobe Illustrator for Vector Graphics',
                        'content': 'Illustrator is the go-to tool for creating scalable vector graphics. Learn the pen tool, shape building, pathfinder operations, and working with bezier curves. Create logos, icons, illustrations, and infographics. Master the appearance panel, graphic styles, and symbols. Understand the difference between raster and vector graphics. Learn to create patterns, gradients, and use the brush tools effectively.',
                        'video_url': 'https://www.youtube.com/embed/Ib8UBwu3yGA',
                        'quiz': {
                            'title': 'Vector Graphics Quiz',
                            'questions': [
                                {
                                    'question': 'What is the main advantage of vector graphics over raster?',
                                    'option_a': 'Better colors',
                                    'option_b': 'Scalability without quality loss',
                                    'option_c': 'Smaller file size',
                                    'option_d': 'Faster rendering',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which tool is primarily used to create custom shapes in Illustrator?',
                                    'option_a': 'Brush tool',
                                    'option_b': 'Pen tool',
                                    'option_c': 'Type tool',
                                    'option_d': 'Gradient tool',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Brand Identity Design',
                        'content': 'Brand identity is the visual expression of a company. Learn to conduct client research, create mood boards, and develop brand strategies. Design complete brand identities including logos, color palettes, typography systems, and brand guidelines. Understand logo types: wordmarks, lettermarks, pictorial marks, abstract marks, mascots, and emblems. Create mockups, business cards, letterheads, and social media templates.',
                        'video_url': 'https://www.youtube.com/embed/U_R4761bxs8',
                        'assignment': {
                            'title': 'Complete Brand Identity Package',
                            'description': 'Create a comprehensive brand identity for a fictional company of your choice. Include: logo in multiple variations, color palette with hex codes, typography system, business card design, letterhead, and a 5-page brand guidelines document. Submit all files organized in a professional manner.'
                        }
                    }
                ]
            },
            {
                'title': 'Robotics for Beginners',
                'description': 'Build and program robots from scratch. Learn electronics, mechanical design, sensors, motors, and autonomous navigation using Arduino and Raspberry Pi.',
                'price_ngn': 50000,
                'price_usd': 35,
                'image_url': 'https://images.unsplash.com/photo-1561557944-6e7860d1a7eb?w=400',
                'modules': [
                    {
                        'title': 'Introduction to Robotics',
                        'content': 'Robotics combines mechanical engineering, electrical engineering, and computer science. Understand the components of a robot: sensors, actuators, controllers, and power supply. Learn about different types of robots: mobile robots, manipulators, humanoids, drones. Explore robotics applications in manufacturing, healthcare, space exploration, and everyday life. Study the history of robotics from early automatons to modern AI-powered robots.',
                        'video_url': 'https://www.youtube.com/embed/bLKJ16wpRGE',
                        'quiz': {
                            'title': 'Robotics Fundamentals Quiz',
                            'questions': [
                                {
                                    'question': 'What are the three main components of a robot?',
                                    'option_a': 'Sensors, Actuators, Controller',
                                    'option_b': 'CPU, RAM, Storage',
                                    'option_c': 'Input, Output, Process',
                                    'option_d': 'Power, Speed, Accuracy',
                                    'correct_answer': 'A'
                                },
                                {
                                    'question': 'What is an actuator in robotics?',
                                    'option_a': 'A device that detects environment',
                                    'option_b': 'A device that causes movement',
                                    'option_c': 'A processing unit',
                                    'option_d': 'A power source',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Arduino Programming & Electronics',
                        'content': 'Arduino is an open-source microcontroller platform perfect for robotics. Learn to write Arduino code (C/C++), understand digital and analog I/O, PWM signals, and serial communication. Master basic electronics: resistors, LEDs, buttons, potentiometers. Build circuits on breadboards, read schematics, and use multimeters. Control LEDs, read sensors, and create interactive projects. Understand the Arduino ecosystem: Uno, Mega, Nano, and shields.',
                        'video_url': 'https://www.youtube.com/embed/nL34zDTPkcs',
                        'assignment': {
                            'title': 'Arduino Traffic Light System',
                            'description': 'Build a traffic light controller using Arduino, LEDs (red, yellow, green), and a button for pedestrian crossing. Implement proper timing sequences and emergency override functionality. Submit your circuit diagram, code with comments, and a video demonstration.'
                        }
                    },
                    {
                        'title': 'Motors & Motion Control',
                        'content': 'Motors are the muscles of robots. Learn about DC motors, servo motors, and stepper motors - their differences, applications, and control methods. Understand motor drivers (L298N, L293D) and H-bridges. Program precise servo control for robotic arms. Implement speed control using PWM. Learn about encoders for position feedback, PID control for accurate motion, and motor power calculations.',
                        'video_url': 'https://www.youtube.com/embed/0qwrnUeSpYQ',
                        'quiz': {
                            'title': 'Motor Control Quiz',
                            'questions': [
                                {
                                    'question': 'Which motor type provides the most precise angle control?',
                                    'option_a': 'DC Motor',
                                    'option_b': 'Servo Motor',
                                    'option_c': 'AC Motor',
                                    'option_d': 'Universal Motor',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'What does PWM stand for?',
                                    'option_a': 'Power Wave Modulation',
                                    'option_b': 'Pulse Width Modulation',
                                    'option_c': 'Precise Wave Movement',
                                    'option_d': 'Programmed Wire Module',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Sensors & Autonomous Navigation',
                        'content': 'Sensors are the eyes and ears of robots. Master ultrasonic sensors (HC-SR04) for distance measurement, IR sensors for line following, IMU (gyroscope + accelerometer) for orientation, and camera modules. Learn obstacle avoidance algorithms, line following logic, and maze-solving strategies. Implement sensor fusion to combine multiple sensor data. Create autonomous robots that navigate without human intervention.',
                        'video_url': 'https://www.youtube.com/embed/y_mJ6dPQbj4',
                        'assignment': {
                            'title': 'Obstacle Avoiding Robot',
                            'description': 'Build a robot that autonomously navigates a room while avoiding obstacles. Use ultrasonic sensors, DC motors with motor driver, and Arduino. Implement logic for detection, decision making, and smooth turning. Submit code, wiring diagram, and demonstration video showing the robot successfully avoiding at least 5 obstacles.'
                        }
                    }
                ]
            },
            {
                'title': 'Electronic Engineering Foundation',
                'description': 'Master electronics from theory to practice. Learn circuit design, microcontrollers, PCB design, and build real-world electronic projects.',
                'price_ngn': 40000,
                'price_usd': 28,
                'image_url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400',
                'modules': [
                    {
                        'title': 'Circuit Theory & Analysis',
                        'content': "Master the fundamentals of electronics. Learn Ohm's Law (V=IR), Kirchhoff's Current and Voltage Laws, series and parallel circuits. Understand resistors (color codes, power ratings), capacitors (types, charging/discharging), inductors, and diodes. Calculate voltage dividers, current dividers, and equivalent resistance. Use Thevenin and Norton theorems for circuit simplification. Analyze AC and DC circuits, understand impedance, and work with RLC circuits.",
                        'video_url': 'https://www.youtube.com/embed/m4jzgqZu-4s',
                        'quiz': {
                            'title': 'Circuit Theory Quiz',
                            'questions': [
                                {
                                    'question': "According to Ohm's Law, what happens to current if voltage doubles and resistance stays constant?",
                                    'option_a': 'Current doubles',
                                    'option_b': 'Current halves',
                                    'option_c': 'Current stays the same',
                                    'option_d': 'Current quadruples',
                                    'correct_answer': 'A'
                                },
                                {
                                    'question': "What is the total resistance of two 10Ω resistors in parallel?",
                                    'option_a': '20Ω',
                                    'option_b': '10Ω',
                                    'option_c': '5Ω',
                                    'option_d': '15Ω',
                                    'correct_answer': 'C'
                                },
                                {
                                    'question': 'What does a diode primarily do?',
                                    'option_a': 'Allows current in one direction only',
                                    'option_b': 'Stores electrical charge',
                                    'option_c': 'Amplifies signals',
                                    'option_d': 'Generates light',
                                    'correct_answer': 'A'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Transistors & Amplifiers',
                        'content': 'Transistors are the building blocks of modern electronics. Learn about BJT (Bipolar Junction Transistor) and MOSFET (Metal-Oxide-Semiconductor Field-Effect Transistor). Understand transistor configurations: common emitter, common collector, common base. Design amplifier circuits, calculate gain, and analyze biasing. Learn about operational amplifiers (op-amps), inverting and non-inverting configurations. Build voltage followers, summing amplifiers, and comparators.',
                        'video_url': 'https://www.youtube.com/embed/7ukDKVHnac4',
                        'assignment': {
                            'title': 'Audio Amplifier Design',
                            'description': 'Design and simulate a simple audio amplifier circuit using transistors or op-amps. Calculate component values, draw the complete circuit diagram, and simulate using software like LTSpice or Proteus. Document the design process, calculations, and expected performance specifications.'
                        }
                    },
                    {
                        'title': 'Microcontrollers & Embedded Systems',
                        'content': 'Microcontrollers are computers on a chip. Deep dive into microcontroller architecture: CPU, memory (RAM, ROM, Flash), I/O ports, timers, interrupts, and communication protocols (UART, SPI, I2C). Learn to program ESP32 and STM32 microcontrollers. Master interrupt handling, timer programming, and power management. Interface with displays (LCD, OLED), sensors, and communication modules (WiFi, Bluetooth). Develop embedded C programming skills.',
                        'video_url': 'https://www.youtube.com/embed/nL34zDTPkcs',
                        'quiz': {
                            'title': 'Microcontrollers Quiz',
                            'questions': [
                                {
                                    'question': 'Which communication protocol uses only two wires (SDA and SCL)?',
                                    'option_a': 'UART',
                                    'option_b': 'SPI',
                                    'option_c': 'I2C',
                                    'option_d': 'USB',
                                    'correct_answer': 'C'
                                },
                                {
                                    'question': 'What is the purpose of an interrupt in microcontrollers?',
                                    'option_a': 'To pause execution and handle urgent events',
                                    'option_b': 'To slow down the processor',
                                    'option_c': 'To increase memory',
                                    'option_d': 'To power off the device',
                                    'correct_answer': 'A'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'PCB Design & Soldering',
                        'content': 'Transform circuits from breadboard to professional PCBs. Learn PCB design using KiCad or Eagle: schematic capture, component placement, routing traces, ground planes, and design rule checking. Understand PCB layers, vias, pads, and silk screen. Master soldering techniques: through-hole and surface mount (SMD). Use proper tools: soldering iron, solder wick, flux, helping hands. Learn desoldering, rework, and quality inspection. Design multi-layer PCBs for complex projects.',
                        'video_url': 'https://www.youtube.com/embed/VxMV6wGS3NY',
                        'assignment': {
                            'title': 'Complete PCB Design Project',
                            'description': 'Design a PCB for an Arduino-based temperature monitoring system with LCD display and sensor. Create schematic, design the PCB layout with proper trace widths, add silk screen labels, and generate Gerber files for manufacturing. Submit all design files, BOM (Bill of Materials), and 3D render of the PCB.'
                        }
                    }
                ]
            },
            {
                'title': 'Data Science & Machine Learning',
                'description': 'Master data analysis, visualization, and machine learning. Learn Python, pandas, scikit-learn, and deploy ML models for real-world applications.',
                'price_ngn': 55000,
                'price_usd': 40,
                'image_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400',
                'modules': [
                    {
                        'title': 'Python for Data Science',
                        'content': 'Python is the language of data science. Master Python fundamentals: variables, data types, control structures, functions, and object-oriented programming. Learn NumPy for numerical computing with arrays and matrices. Master Pandas for data manipulation: DataFrames, Series, indexing, filtering, groupby, merge, and pivot tables. Handle missing data, data cleaning, and data transformation. Read and write various file formats: CSV, Excel, JSON, SQL databases.',
                        'video_url': 'https://www.youtube.com/embed/LHBE6Q9XlzI',
                        'quiz': {
                            'title': 'Python Data Science Quiz',
                            'questions': [
                                {
                                    'question': 'Which library is best for handling tabular data in Python?',
                                    'option_a': 'NumPy',
                                    'option_b': 'Pandas',
                                    'option_c': 'Matplotlib',
                                    'option_d': 'Requests',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'What is a DataFrame in Pandas?',
                                    'option_a': 'A single column of data',
                                    'option_b': 'A 2D labeled data structure',
                                    'option_c': 'A plotting function',
                                    'option_d': 'A machine learning model',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which method is used to remove rows with missing values in Pandas?',
                                    'option_a': 'remove_na()',
                                    'option_b': 'delete_missing()',
                                    'option_c': 'dropna()',
                                    'option_d': 'clean_data()',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Data Visualization & Analysis',
                        'content': 'Turn data into insights through visualization. Master Matplotlib for creating plots: line plots, scatter plots, bar charts, histograms, pie charts. Learn Seaborn for statistical visualizations: distribution plots, regression plots, categorical plots, heatmaps. Create interactive visualizations with Plotly. Understand when to use each chart type. Learn exploratory data analysis (EDA): descriptive statistics, correlation analysis, outlier detection. Create compelling data stories.',
                        'video_url': 'https://www.youtube.com/embed/DAQNHzOcO5A',
                        'assignment': {
                            'title': 'Comprehensive Data Analysis Report',
                            'description': 'Analyze a real-world dataset (provided or choose from Kaggle). Perform complete EDA including data cleaning, statistical analysis, and create at least 8 different visualizations. Write a detailed report with insights, patterns discovered, and recommendations. Submit Jupyter notebook and PDF report.'
                        }
                    },
                    {
                        'title': 'Machine Learning Fundamentals',
                        'content': 'Introduction to ML: supervised vs unsupervised learning, regression vs classification. Learn key algorithms: Linear Regression, Logistic Regression, Decision Trees, Random Forests, K-Nearest Neighbors, K-Means Clustering. Understand the ML workflow: data preprocessing, train-test split, feature scaling, model training, evaluation metrics (accuracy, precision, recall, F1-score, RMSE). Use scikit-learn for implementation. Handle overfitting and underfitting with cross-validation.',
                        'video_url': 'https://www.youtube.com/embed/ukzFI9rgwfU',
                        'quiz': {
                            'title': 'Machine Learning Quiz',
                            'questions': [
                                {
                                    'question': 'What type of learning uses labeled training data?',
                                    'option_a': 'Unsupervised Learning',
                                    'option_b': 'Supervised Learning',
                                    'option_c': 'Reinforcement Learning',
                                    'option_d': 'Transfer Learning',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which algorithm is used for clustering?',
                                    'option_a': 'Linear Regression',
                                    'option_b': 'Logistic Regression',
                                    'option_c': 'K-Means',
                                    'option_d': 'Decision Tree',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Deep Learning & Neural Networks',
                        'content': 'Neural networks are inspired by the human brain. Understand perceptrons, activation functions (ReLU, sigmoid, tanh), forward and backward propagation. Learn to build neural networks with TensorFlow and Keras. Master CNNs (Convolutional Neural Networks) for image classification, RNNs (Recurrent Neural Networks) for sequence data. Implement transfer learning with pre-trained models (VGG, ResNet). Deploy models using Flask or FastAPI.',
                        'video_url': 'https://www.youtube.com/embed/aircAruvnKk',
                        'assignment': {
                            'title': 'Image Classification Project',
                            'description': 'Build a CNN model to classify images from a dataset (e.g., CIFAR-10 or cats vs dogs). Implement data augmentation, train the model, achieve at least 80% accuracy, and create a simple web interface to upload and classify new images. Submit code, trained model, and demonstration video.'
                        }
                    }
                ]
            },
            {
                'title': 'Full Stack Web Development',
                'description': 'Build complete web applications from scratch. Master HTML, CSS, JavaScript, React, Node.js, databases, and deployment.',
                'price_ngn': 60000,
                'price_usd': 45,
                'image_url': 'https://images.unsplash.com/photo-1547658719-da2b51169166?w=400',
                'modules': [
                    {
                        'title': 'HTML5 & CSS3 Fundamentals',
                        'content': 'HTML is the structure of the web. Master semantic HTML5 tags: header, nav, main, article, section, footer. Learn forms, tables, media elements. CSS brings style to the web: selectors, specificity, box model, display properties, positioning (static, relative, absolute, fixed, sticky). Master Flexbox and CSS Grid for layouts. Learn responsive design with media queries, mobile-first approach. Understand CSS preprocessors (SASS/SCSS) and CSS frameworks (Bootstrap, Tailwind CSS).',
                        'video_url': 'https://www.youtube.com/embed/hu-q2zYwEYs',
                        'quiz': {
                            'title': 'HTML & CSS Quiz',
                            'questions': [
                                {
                                    'question': 'Which HTML5 tag is used for independent content?',
                                    'option_a': '<div>',
                                    'option_b': '<section>',
                                    'option_c': '<article>',
                                    'option_d': '<span>',
                                    'correct_answer': 'C'
                                },
                                {
                                    'question': 'What does the CSS property "display: flex" enable?',
                                    'option_a': 'Grid layout',
                                    'option_b': 'Flexbox layout',
                                    'option_c': 'Block layout',
                                    'option_d': 'Table layout',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which CSS unit is relative to the viewport width?',
                                    'option_a': 'px',
                                    'option_b': 'em',
                                    'option_c': 'vw',
                                    'option_d': 'pt',
                                    'correct_answer': 'C'
                                }
                            ]
                        },
                        'assignment': {
                            'title': 'Responsive Portfolio Website',
                            'description': 'Create a fully responsive personal portfolio website using HTML5 and CSS3. Include: navigation, hero section, about, projects grid, contact form, and footer. Must be mobile-responsive and use Flexbox or Grid. No frameworks allowed. Submit code and live demo link.'
                        }
                    },
                    {
                        'title': 'JavaScript & DOM Manipulation',
                        'content': 'JavaScript makes web pages interactive. Master ES6+ features: let/const, arrow functions, destructuring, spread operator, promises, async/await. Learn DOM manipulation: selecting elements, event listeners, creating/modifying elements. Understand closures, scope, hoisting, and the event loop. Work with APIs using Fetch and Axios. Handle JSON data. Learn localStorage, sessionStorage, and cookies. Implement form validation, animations, and dynamic content loading.',
                        'video_url': 'https://www.youtube.com/embed/hdI2bqOjy3c',
                        'quiz': {
                            'title': 'JavaScript Quiz',
                            'questions': [
                                {
                                    'question': 'What is the difference between let and var?',
                                    'option_a': 'No difference',
                                    'option_b': 'let has block scope, var has function scope',
                                    'option_c': 'var is newer than let',
                                    'option_d': 'let is faster than var',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which method is used to add an event listener?',
                                    'option_a': 'attachEvent()',
                                    'option_b': 'on()',
                                    'option_c': 'addEventListener()',
                                    'option_d': 'bind()',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'React.js Frontend Development',
                        'content': 'React is a powerful library for building user interfaces. Learn components (functional and class), JSX syntax, props, state management with useState and useReducer. Master React hooks: useEffect, useContext, useRef, useMemo, useCallback. Build reusable components, implement routing with React Router, manage global state with Context API or Redux. Learn form handling with Formik, API integration, and component lifecycle. Style components with CSS Modules, styled-components, or Material-UI.',
                        'video_url': 'https://www.youtube.com/embed/w7ejDZ8SWv8',
                        'assignment': {
                            'title': 'React Task Manager App',
                            'description': 'Build a task manager application using React. Features: add/edit/delete tasks, mark as complete, filter (all/active/completed), persist data to localStorage, responsive design. Use React hooks, implement proper component structure, and add at least one external library (e.g., date picker). Submit GitHub repository with README.'
                        }
                    },
                    {
                        'title': 'Backend with Node.js & Databases',
                        'content': 'Node.js enables JavaScript on the server. Learn Express.js framework: routing, middleware, error handling, authentication (JWT, sessions). Build RESTful APIs with proper HTTP methods (GET, POST, PUT, DELETE). Master databases: MongoDB (NoSQL) with Mongoose, PostgreSQL/MySQL (SQL) with Sequelize. Implement CRUD operations, data validation, and relationships. Learn authentication, authorization, password hashing with bcrypt. Deploy applications to cloud platforms (Heroku, Vercel, Railway).',
                        'video_url': 'https://www.youtube.com/embed/Oe421EPjeBE',
                        'assignment': {
                            'title': 'Full Stack Blog Application',
                            'description': 'Create a complete blog application with React frontend and Node.js backend. Features: user authentication, create/edit/delete posts, comments, user profiles, image uploads. Use MongoDB or PostgreSQL. Implement proper error handling, validation, and security measures. Deploy both frontend and backend. Submit GitHub repo and live demo links.'
                        }
                    }
                ]
            },
            {
                'title': 'Mobile App Development with Flutter',
                'description': 'Build beautiful native mobile apps for iOS and Android using Flutter and Dart. Learn UI design, state management, and app deployment.',
                'price_ngn': 48000,
                'price_usd': 32,
                'image_url': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400',
                'modules': [
                    {
                        'title': 'Dart Programming Language',
                        'content': 'Dart is the language behind Flutter. Learn Dart fundamentals: variables, data types, operators, control flow (if/else, switch, loops). Master functions, classes, objects, inheritance, and mixins. Understand null safety, generics, and asynchronous programming with Future and async/await. Learn collections: List, Set, Map. Explore packages and the pub package manager. Write clean, maintainable Dart code following best practices.',
                        'video_url': 'https://www.youtube.com/embed/Ej_Pcr4uC2Q',
                        'quiz': {
                            'title': 'Dart Basics Quiz',
                            'questions': [
                                {
                                    'question': 'What keyword is used to define a class in Dart?',
                                    'option_a': 'def',
                                    'option_b': 'class',
                                    'option_c': 'type',
                                    'option_d': 'struct',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which keyword makes a variable nullable in Dart?',
                                    'option_a': 'null',
                                    'option_b': 'optional',
                                    'option_c': '?',
                                    'option_d': 'maybe',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Flutter UI Development',
                        'content': 'Everything in Flutter is a widget. Learn core widgets: Container, Row, Column, Stack, ListView, GridView, Text, Image, Button. Master layout widgets and constraints. Understand StatelessWidget vs StatefulWidget. Create beautiful UIs with Material Design and Cupertino (iOS-style) widgets. Learn navigation and routing between screens. Implement forms, validation, and user input handling. Use themes for consistent styling across the app.',
                        'video_url': 'https://www.youtube.com/embed/x0uinJvhNxI',
                        'assignment': {
                            'title': 'E-Commerce Product Catalog UI',
                            'description': 'Create a product catalog UI for an e-commerce app. Include: grid view of products with images, product detail screen, shopping cart, bottom navigation bar, search functionality, and category filters. Focus on beautiful UI with smooth animations. Submit code and APK or demo video.'
                        }
                    },
                    {
                        'title': 'State Management & APIs',
                        'content': 'State management is crucial for complex apps. Learn setState for simple state, Provider for app-wide state, and Riverpod for advanced patterns. Understand when to use each approach. Integrate REST APIs using the http package. Parse JSON data, handle loading states, and error handling. Implement local data persistence with SharedPreferences and SQLite. Learn to manage app lifecycle and background processes.',
                        'video_url': 'https://www.youtube.com/embed/3tm-R7ymwhc',
                        'quiz': {
                            'title': 'State Management Quiz',
                            'questions': [
                                {
                                    'question': 'Which state management solution is built into Flutter?',
                                    'option_a': 'Provider',
                                    'option_b': 'setState',
                                    'option_c': 'Riverpod',
                                    'option_d': 'BLoC',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'What package is commonly used for HTTP requests in Flutter?',
                                    'option_a': 'fetch',
                                    'option_b': 'axios',
                                    'option_c': 'http',
                                    'option_d': 'requests',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Firebase Integration & Deployment',
                        'content': 'Firebase is a complete backend solution for mobile apps. Integrate Firebase Authentication for user login (email/password, Google, Facebook). Use Cloud Firestore for real-time database. Implement Firebase Storage for images and files. Add push notifications with Firebase Cloud Messaging (FCM). Learn analytics, crash reporting, and performance monitoring. Deploy apps to Google Play Store and Apple App Store. Understand app signing, versioning, and release management.',
                        'video_url': 'https://www.youtube.com/embed/sfA3NWDBPZ4',
                        'assignment': {
                            'title': 'Complete Social Media App',
                            'description': 'Build a simple social media app with Firebase backend. Features: user authentication, create posts with images, like/comment on posts, user profiles, real-time updates. Use Firebase Auth, Firestore, and Storage. Implement proper security rules. Submit complete source code, Firebase configuration, and demo video showing all features.'
                        }
                    }
                ]
            },
            {
                'title': '3D Modeling & Animation with Blender',
                'description': 'Master 3D modeling, texturing, lighting, and animation. Create stunning 3D art for games, films, and product visualization.',
                'price_ngn': 42000,
                'price_usd': 30,
                'image_url': 'https://images.unsplash.com/photo-1633412802994-5c058f151b6e?w=400',
                'modules': [
                    {
                        'title': 'Blender Interface & Modeling Basics',
                        'content': 'Blender is a powerful free 3D creation suite. Master the interface: viewport navigation, object mode vs edit mode, add-ons. Learn fundamental modeling techniques: extrude, inset, bevel, loop cuts, subdivision surface. Create basic shapes and transform them into complex objects. Understand vertices, edges, and faces. Learn modifier stack, proportional editing, and snapping tools. Model everyday objects to build your skills.',
                        'video_url': 'https://www.youtube.com/embed/nIoXOplUvAw',
                        'quiz': {
                            'title': 'Blender Basics Quiz',
                            'questions': [
                                {
                                    'question': 'What key activates the search menu in Blender?',
                                    'option_a': 'Tab',
                                    'option_b': 'Spacebar',
                                    'option_c': 'F3',
                                    'option_d': 'Ctrl+F',
                                    'correct_answer': 'C'
                                },
                                {
                                    'question': 'Which mode allows you to edit individual vertices?',
                                    'option_a': 'Object Mode',
                                    'option_b': 'Edit Mode',
                                    'option_c': 'Sculpt Mode',
                                    'option_d': 'Texture Paint',
                                    'correct_answer': 'B'
                                }
                            ]
                        },
                        'assignment': {
                            'title': 'Product Modeling Project',
                            'description': 'Model a realistic everyday object (e.g., coffee mug, water bottle, smartphone). Focus on clean topology, proper proportions, and attention to detail. Submit .blend file and rendered images from multiple angles showing wireframe and solid views.'
                        }
                    },
                    {
                        'title': 'Materials, Texturing & UV Unwrapping',
                        'content': 'Make your models look realistic with materials and textures. Learn the Shader Editor: Principled BSDF, image textures, procedural textures. Master UV unwrapping: mark seams, unwrap methods, texture painting. Understand PBR (Physically Based Rendering) workflow: base color, metallic, roughness, normal maps. Use texture atlas and optimize UV layouts. Create materials for different surfaces: metal, plastic, wood, fabric, glass.',
                        'video_url': 'https://www.youtube.com/embed/0r-cGjVKvGw',
                        'quiz': {
                            'title': 'Texturing Quiz',
                            'questions': [
                                {
                                    'question': 'What does UV unwrapping do?',
                                    'option_a': 'Adds color to models',
                                    'option_b': 'Flattens 3D surface to 2D for texturing',
                                    'option_c': 'Creates animations',
                                    'option_d': 'Adds lighting',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which shader is the standard for PBR materials in Blender?',
                                    'option_a': 'Diffuse BSDF',
                                    'option_b': 'Glossy BSDF',
                                    'option_c': 'Principled BSDF',
                                    'option_d': 'Emission',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Lighting, Rendering & Compositing',
                        'content': 'Lighting brings your scenes to life. Learn different light types: point, sun, spot, area. Master HDRI lighting for realistic environments. Understand 3-point lighting setup. Use Cycles and Eevee render engines. Configure render settings for quality vs speed. Learn the Compositor for post-processing: color grading, glare, depth of field, bloom effects. Render animations and image sequences. Optimize render times.',
                        'video_url': 'https://www.youtube.com/embed/Rr51z8yWPhs',
                        'assignment': {
                            'title': 'Product Visualization Render',
                            'description': 'Create a professional product visualization scene. Set up studio lighting, add an environment, create camera angles, and render a final image suitable for advertising. Include at least 3 different material types. Submit final rendered image (4K resolution) and .blend file.'
                        }
                    },
                    {
                        'title': 'Character Animation & Rigging',
                        'content': 'Bring characters to life with animation. Learn armature (skeleton) creation, bone placement, and hierarchy. Master rigging: FK (Forward Kinematics) vs IK (Inverse Kinematics), constraints, bone weight painting. Create walk cycles, run cycles, and action sequences. Understand the timeline, keyframes, and the graph editor. Learn animation principles: timing, spacing, squash and stretch, anticipation. Use NLA (Non-Linear Animation) editor for complex animations.',
                        'video_url': 'https://www.youtube.com/embed/f3Cr8Yx3GGA',
                        'assignment': {
                            'title': 'Character Walk Cycle Animation',
                            'description': 'Create a rigged humanoid character and animate a realistic walk cycle. The animation should loop seamlessly and demonstrate understanding of weight, balance, and timing. Submit .blend file with completed rig and animation, plus rendered animation video (MP4, minimum 10 seconds).'
                        }
                    }
                ]
            },
            {
                'title': 'Digital Marketing & SEO Mastery',
                'description': 'Master digital marketing strategies, SEO, content marketing, social media, and analytics to grow businesses online.',
                'price_ngn': 38000,
                'price_usd': 27,
                'image_url': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400',
                'modules': [
                    {
                        'title': 'Digital Marketing Fundamentals',
                        'content': 'Digital marketing is essential for modern businesses. Learn the marketing funnel: awareness, consideration, conversion, loyalty. Understand different channels: search engines, social media, email, content marketing, paid advertising. Learn target audience research, buyer personas, and customer journey mapping. Study marketing metrics: CTR, conversion rate, ROI, CAC, LTV. Develop comprehensive digital marketing strategies aligned with business goals.',
                        'video_url': 'https://www.youtube.com/embed/nU-IIXBWlS4',
                        'quiz': {
                            'title': 'Digital Marketing Quiz',
                            'questions': [
                                {
                                    'question': 'What does CTR stand for in digital marketing?',
                                    'option_a': 'Cost To Revenue',
                                    'option_b': 'Click Through Rate',
                                    'option_c': 'Customer Transaction Record',
                                    'option_d': 'Content Traffic Rank',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which stage comes first in the marketing funnel?',
                                    'option_a': 'Conversion',
                                    'option_b': 'Consideration',
                                    'option_c': 'Awareness',
                                    'option_d': 'Loyalty',
                                    'correct_answer': 'C'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'SEO (Search Engine Optimization)',
                        'content': 'SEO drives organic traffic to websites. Master on-page SEO: keyword research with tools (Google Keyword Planner, Ahrefs), title tags, meta descriptions, header tags, URL structure, internal linking. Learn technical SEO: site speed, mobile optimization, XML sitemaps, robots.txt, schema markup. Understand off-page SEO: backlink building, domain authority, guest posting. Use Google Search Console and Google Analytics. Learn local SEO for businesses. Stay updated with algorithm changes.',
                        'video_url': 'https://www.youtube.com/embed/xsVTqzratPs',
                        'assignment': {
                            'title': 'Complete SEO Audit Report',
                            'description': 'Conduct a comprehensive SEO audit for a real website (your own or a volunteer business). Analyze technical SEO, on-page factors, backlink profile, and competitors. Use tools like Screaming Frog, Google Search Console. Provide actionable recommendations with priority levels. Submit a professional PDF report with screenshots and data visualizations.'
                        }
                    },
                    {
                        'title': 'Social Media Marketing',
                        'content': 'Social media connects brands with audiences. Master platform-specific strategies: Facebook (community building), Instagram (visual storytelling), Twitter (real-time engagement), LinkedIn (B2B networking), TikTok (viral content). Learn content creation: copywriting, visual design, video editing. Understand hashtag strategies, posting schedules, and engagement tactics. Use social media management tools (Hootsuite, Buffer). Run paid social campaigns. Measure success with platform analytics.',
                        'video_url': 'https://www.youtube.com/embed/tVH1kW1a11g',
                        'quiz': {
                            'title': 'Social Media Quiz',
                            'questions': [
                                {
                                    'question': 'Which social media platform is best for B2B marketing?',
                                    'option_a': 'TikTok',
                                    'option_b': 'Instagram',
                                    'option_c': 'LinkedIn',
                                    'option_d': 'Snapchat',
                                    'correct_answer': 'C'
                                },
                                {
                                    'question': 'What is the optimal posting frequency on Instagram for engagement?',
                                    'option_a': 'Once per month',
                                    'option_b': '1-2 times per day',
                                    'option_c': '10 times per day',
                                    'option_d': 'Once per week',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Content Marketing & Email Campaigns',
                        'content': 'Content is king in digital marketing. Learn content strategy: blog posts, videos, infographics, podcasts, ebooks. Master storytelling and creating valuable content that attracts and retains audiences. Build email lists and segment audiences. Design effective email campaigns: welcome series, newsletters, promotional emails, abandoned cart sequences. Learn email marketing platforms (Mailchimp, ConvertKit). Write compelling subject lines and CTAs. Understand deliverability, A/B testing, and automation workflows. Track open rates, click rates, and conversions.',
                        'video_url': 'https://www.youtube.com/embed/Jq1VTHzb_Hc',
                        'assignment': {
                            'title': 'Content Marketing Campaign',
                            'description': 'Create a 30-day content marketing plan for a business. Include: content calendar with topics, formats (blog, video, social), distribution channels, email sequence (5 emails), and KPIs to track. Write 2 complete blog posts (1000+ words each) and design 3 social media graphics. Submit complete plan document, blog posts, and graphics.'
                        }
                    }
                ]
            },
            {
                'title': 'Cloud Computing with AWS',
                'description': 'Master Amazon Web Services (AWS) from basics to advanced. Learn EC2, S3, Lambda, databases, and deploy scalable cloud applications.',
                'price_ngn': 52000,
                'price_usd': 38,
                'image_url': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400',
                'modules': [
                    {
                        'title': 'AWS Fundamentals & Cloud Concepts',
                        'content': 'Cloud computing delivers computing services over the internet. Understand cloud models: IaaS, PaaS, SaaS. Learn AWS global infrastructure: regions, availability zones, edge locations. Master the AWS Management Console, AWS CLI, and CloudShell. Understand the shared responsibility model. Learn about IAM (Identity and Access Management): users, groups, roles, policies, MFA. Explore AWS Free Tier and cost management. Study AWS Well-Architected Framework: operational excellence, security, reliability, performance efficiency, cost optimization.',
                        'video_url': 'https://www.youtube.com/embed/ulprqHHWlng',
                        'quiz': {
                            'title': 'AWS Basics Quiz',
                            'questions': [
                                {
                                    'question': 'What does IAM stand for?',
                                    'option_a': 'Internet Access Management',
                                    'option_b': 'Identity and Access Management',
                                    'option_c': 'Internal Application Monitor',
                                    'option_d': 'Instance Allocation Manager',
                                    'correct_answer': 'B'
                                },
                                {
                                    'question': 'Which AWS service provides object storage?',
                                    'option_a': 'EC2',
                                    'option_b': 'RDS',
                                    'option_c': 'S3',
                                    'option_d': 'Lambda',
                                    'correct_answer': 'C'
                                },
                                {
                                    'question': 'What is an Availability Zone in AWS?',
                                    'option_a': 'A country',
                                    'option_b': 'A data center or group of data centers',
                                    'option_c': 'A network protocol',
                                    'option_d': 'A security feature',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'EC2 & Compute Services',
                        'content': 'EC2 (Elastic Compute Cloud) provides virtual servers in the cloud. Learn instance types: general purpose, compute optimized, memory optimized, storage optimized. Master AMIs (Amazon Machine Images), security groups, and key pairs. Understand EBS (Elastic Block Store) volumes, snapshots, and IOPS. Learn Auto Scaling groups and Elastic Load Balancing. Explore AWS Lambda for serverless computing. Deploy applications, configure monitoring with CloudWatch, and implement backup strategies.',
                        'video_url': 'https://www.youtube.com/embed/8TlukLu11Yo',
                        'assignment': {
                            'title': 'Deploy Web Application on EC2',
                            'description': 'Launch an EC2 instance, configure security groups, deploy a web application (Node.js or Python Flask), set up a load balancer, and configure auto-scaling. Implement CloudWatch monitoring and alarms. Document the entire process with screenshots, architecture diagram, and access instructions. Submit documentation and the public URL.'
                        }
                    },
                    {
                        'title': 'Storage & Database Services',
                        'content': 'AWS offers various storage and database solutions. Master S3 (Simple Storage Service): buckets, objects, versioning, lifecycle policies, encryption, static website hosting. Learn S3 storage classes: Standard, Intelligent-Tiering, Glacier. Explore RDS (Relational Database Service) for MySQL, PostgreSQL, SQL Server. Understand DynamoDB for NoSQL. Learn Aurora, ElastiCache for Redis/Memcached. Implement database backups, replication, and read replicas.',
                        'video_url': 'https://www.youtube.com/embed/Ia-UEYYR44s',
                        'quiz': {
                            'title': 'AWS Storage & Database Quiz',
                            'questions': [
                                {
                                    'question': 'Which S3 storage class is best for infrequently accessed data?',
                                    'option_a': 'S3 Standard',
                                    'option_b': 'S3 Intelligent-Tiering',
                                    'option_c': 'S3 Glacier',
                                    'option_d': 'S3 One Zone-IA',
                                    'correct_answer': 'C'
                                },
                                {
                                    'question': 'What type of database is DynamoDB?',
                                    'option_a': 'Relational',
                                    'option_b': 'NoSQL',
                                    'option_c': 'Graph',
                                    'option_d': 'Time-series',
                                    'correct_answer': 'B'
                                }
                            ]
                        }
                    },
                    {
                        'title': 'Networking, Security & DevOps',
                        'content': 'Build secure and scalable cloud architectures. Master VPC (Virtual Private Cloud): subnets, route tables, internet gateways, NAT gateways. Learn security: Security Groups, NACLs, AWS WAF, AWS Shield. Understand CloudFront CDN for content delivery. Explore Route 53 for DNS management. Learn DevOps practices: CodePipeline, CodeBuild, CodeDeploy for CI/CD. Use CloudFormation for Infrastructure as Code. Implement monitoring with CloudWatch and AWS X-Ray. Study cost optimization strategies.',
                        'video_url': 'https://www.youtube.com/embed/hiKPPy584Mg',
                        'assignment': {
                            'title': 'Complete Cloud Architecture Project',
                            'description': 'Design and deploy a complete 3-tier web application on AWS. Include: VPC with public and private subnets, EC2 instances with auto-scaling, RDS database in private subnet, S3 for static assets, CloudFront distribution, Route 53 DNS, and CI/CD pipeline. Create architecture diagram, CloudFormation template, and comprehensive documentation. Submit all files and live demo URL.'
                        }
                    }
                ]
            }
        ]
        
        for course_data in courses_data:
            course = Course(
                title=course_data['title'],
                description=course_data['description'],
                price_ngn=course_data['price_ngn'],
                price_usd=course_data['price_usd'],
                image_url=course_data['image_url']
            )
            db.session.add(course)
            db.session.flush()
            
            for idx, module_data in enumerate(course_data['modules']):
                module = Module(
                    course_id=course.id,
                    title=module_data['title'],
                    content=module_data['content'],
                    video_url=module_data.get('video_url', ''),
                    order=idx
                )
                db.session.add(module)
                db.session.flush()
                
                if 'quiz' in module_data:
                    quiz = Quiz(
                        module_id=module.id,
                        title=module_data['quiz']['title']
                    )
                    db.session.add(quiz)
                    db.session.flush()
                    
                    for question_data in module_data['quiz']['questions']:
                        question = QuizQuestion(
                            quiz_id=quiz.id,
                            question=question_data['question'],
                            option_a=question_data['option_a'],
                            option_b=question_data['option_b'],
                            option_c=question_data['option_c'],
                            option_d=question_data['option_d'],
                            correct_answer=question_data['correct_answer']
                        )
                        db.session.add(question)
                
                if 'assignment' in module_data:
                    assignment = Assignment(
                        module_id=module.id,
                        title=module_data['assignment']['title'],
                        description=module_data['assignment']['description']
                    )
                    db.session.add(assignment)
        
        db.session.commit()
        print("Database populated with 10 comprehensive courses successfully!")
    finally:
        if ctx:
            ctx.pop()

if __name__ == '__main__':
    populate_courses()
