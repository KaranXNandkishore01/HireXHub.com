# HirexHub - Intelligent Recruitment & Job Portal

![HirexHub Banner](https://via.placeholder.com/1200x400?text=HirexHub+Intelligent+Recruitment)

**HirexHub** is a next-generation recruitment platform designed to bridge the gap between top-tier talent and world-class opportunities. We leverage advanced technology and AI to streamline the hiring process, making it efficient, transparent, and human-centric.

## 🚀 Key Features

*   **Intelligent Job Matching:** Algorithmic matching of candidates to job descriptions based on skills and experience.
*   **AI Resume Scorer:** Instant feedback on resume strength and relevance to specific job roles.
*   **Role-Based Dashboards:** Dedicated experiences for **Applicants** (Job Seekers) and **Recruiters** (HR).
*   **Dynamic User Interface:** Modern, responsive design with glassmorphism effects and smooth animations.
*   **Secure Authentication:** Robust user registration and login system.
*   **Application Tracking:** Real-time status updates on job applications.

## 🛠️ Technology Stack

*   **Backend:** Django (Python)
*   **Frontend:** HTML5, CSS3, JavaScript (Bootstrap 5)
*   **Database:** SQLite (Default for development)
*   **AI/ML:** *(Mention any specific libraries used like NLTK, spaCy, or custom logic implemented)*

## 📦 Installation & Setup

Follow these steps to get the project running locally on your machine.

### Prerequisites

*   Python 3.8+ installed
*   Git installed

### Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/KaranXNandkishore01/HirexHub.git
    cd HirexHub
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Create a Superuser (Admin)**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```

7.  **Access the Application**
    Open your browser and navigate to `http://127.0.0.1:8000/`.

## 📂 Project Structure

```
HirexHub/
├── job_portal/         # Core project settings
├── recruitment/        # Main app logic (Job listings, Applications)
├── users/              # User management (Auth, Profiles)
├── templates/          # HTML Templates
├── static/             # Static files (CSS, JS, Images)
├── scripts/            # Utility and verification scripts
├── manage.py           # Django command-line utility
└── requirements.txt    # Python dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Built with ❤️ by [Karan Prajapati],[Rohit Lovevanshi] & [Man Mehra])*

