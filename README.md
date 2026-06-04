Render: https://carebridge-rxma.onrender.com/

Neon: https://console.neon.tech/app/projects/quiet-lake-61952324

Github: https://github.com/mariellecabie22-a11y/CareBridge

# CareBridge

## Overview

CareBridge is a Flask-based web application designed to improve the continuity of patient care by providing healthcare professionals with a centralised platform for creating, managing, and accessing patient discharge summaries.

Working in healthcare for over 10 years, I have frequently encountered challenges when caring for patients who have received treatment at multiple hospitals or healthcare facilities. Many patients are unable to recall or fully understand their medical history, diagnoses, medications, or follow-up plans. This often makes it difficult for healthcare professionals to obtain accurate information and provide seamless continuity of care.

To address this issue, I developed CareBridge as a secure and user-friendly platform that allows healthcare workers to document and review patient discharge information in a structured format. By improving access to important clinical information, CareBridge aims to support safer, more informed, and more efficient patient care.

## Features

* Secure user registration and authentication
* Password hashing and account management
* Create, view, edit, and delete discharge summaries
* Patient search functionality
* Mobile-responsive design
* Print-friendly discharge summaries
* Account settings with password update functionality
* PostgreSQL database integration using Neon
* Flask-SQLAlchemy ORM for database management

## Technologies Used

* Python
* Flask
* PostgreSQL
* Neon Database
* SQLAlchemy
* HTML5
* CSS3
* JavaScript
* Render (Deployment)

## Database Structure

### Users

Stores healthcare user account information:

* Full name
* Role (Physician, Nurse, Student)
* Email address
* Password hash

### Patients

Stores patient discharge summary information:

* Patient demographics
* Hospital and ward information
* Diagnosis
* Clinical summary
* Medications
* Follow-up instructions

### Account Settings

Stores user-specific preferences and settings:

* Notification preferences
* Theme preferences
* Last updated timestamp

## Future Improvements

* PDF export functionality
* Multi-hospital integration
* Role-based permissions
* Advanced reporting and analytics
* Secure sharing of discharge summaries between healthcare providers

## Author

Developed by Marielle Cabie as part of a Flask and PostgreSQL web application project, inspired by real-world challenges encountered in healthcare practice.

