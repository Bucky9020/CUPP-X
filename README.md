# 🧠 CUPP-X Ultimate by Bucky

**CUPP-X Ultimate** is an advanced and modern version of the **Common User Passwords Profiler (CUPP)**, redesigned by **Bucky** with a **Dark Tkinter GUI** and smarter wordlist generation logic.  
It helps you generate **highly personalized password wordlists** based on detailed profile inputs — perfect for penetration testing, cybersecurity training, and educational research.

---

## 🚀 Features

- 🖤 **Dark-themed Tkinter GUI**
- ⚙️ **Smart profile expansion** using names, nicknames, partners, pets, companies, and keywords  
- 🔢 **Dynamic combinations** with phone numbers, years, and prefixes/suffixes  
- 💡 **Leet transformation** (e.g., `a -> 4`, `e -> 3`, etc.)
- 🔣 **Symbol injection engine** with customizable probabilities  
- 🎯 **Adjustable target word count** (generate thousands or millions of words)
- 🔁 **Unlimited target profiles** — combine as many fields as you want  
- 🧮 **Optimized algorithm** for balanced performance and randomness
- 💾 **Save generated wordlist** directly from the GUI  
- ✅ **Cross-platform** (Linux, Windows, macOS)

---

## 🧩 Installation

### 1. Clone the repository:
```bash
git clone https://github.com/Bucky9020/CUPP-X.git
cd CUPP-X
```
2. Run the script:
3. Make sure you have Python 3 installed.
4. ```
   python3 CUPP-X.py
   ```
🖥️ GUI Overview
| Section            | Description                                                       |
| ------------------ | ----------------------------------------------------------------- |
| **Profile Fields** | Add personal data such as name, partner, pet, keywords, etc.      |
| **Phone & Email**  | Include digits for deeper word generation.                        |
| **Years / Age**    | Automatically calculates birth years and short forms.             |
| **Leet Mode**      | Enables automatic character replacement (like hacker-style text). |
| **Symbols**        | Optionally inject random or weighted symbols between words.       |
| **Target Words**   | Set how many total combinations to generate.                      |
| **Preview Box**    | Displays first 500 generated passwords.                           |
| **Save Button**    | Exports full wordlist as `.txt` file.                             |

⚙️ Example Usage

Enter the profile info:

First Name: John

Last Name: Doe

Nicknames: johnny, jd

Partner: Alice

Pet: Rocky

Keywords: gaming, hacker

Phone: 01098765432

Age: 23

Enable:
✅ Use leet variants

✅ Enable symbols

Set Max Symbols → 2

Target Words → 5000

Click "Generate Wordlist"

Preview or save the generated list.

🧠 How Symbol Probability Works
You can define how likely symbols appear using a comma-separated list.
Example = 1, 3, 5

If Max symbols = 2, then:

Probability for 0 symbols = 1

Probability for 1 symbol = 3

Probability for 2 symbols = 5
→ Higher values = higher chance of that count appearing.

If left blank → uniform distribution is used.

⚠️ Disclaimer
This project is for educational and ethical cybersecurity use only.
Do not use generated wordlists against systems you do not own or have explicit permission to test.
The author (Bucky) and contributors are not responsible for any misuse.

🧑‍💻 Author
Created by: Bucky

Version: 1.0
Language: Python 3
GUI: Tkinter (Dark mode)

Support
If you like this project, give it a ⭐ on GitHub and share it with others in the cybersecurity community!
