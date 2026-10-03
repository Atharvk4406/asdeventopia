# Jira Agile & Scrum Documentation
## ASDD DevOps Mini Project: AI Event Management System (Eventopia)

---

## 1. Project Overview & Agile Objectives
In accordance with Agile Software Development and DevOps (ASDD) methodologies, this mini-project is structured around iterative development, sprint tracking, and continuous integration.

- **Project Name:** AI Event Management System (Eventopia) & DevOps Pipeline
- **Project Key:** `ASDD`
- **Methodology:** Scrum Framework
- **Sprint Duration:** 2 Weeks (1 Sprint Cycle for Mini-Project)

---

## 2. Jira Epics & User Stories Breakdown

### 🎯 Epic 1: Agile Planning & Version Control (`ASDD-EPIC-1`)
*Objective:* Establish project tracking in Jira, define user stories, and configure GitHub source code management.

| Key | Issue Type | Summary | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| `ASDD-1` | Story | Setup Jira Scrum Board & Sprint Backlog | Epics, User Stories, and Sprint 1 backlog defined. |
| `ASDD-2` | Story | Initialize Git Repository & GitHub Remote | Remote repo created with `main` and `feature` branches. |
| `ASDD-3` | Story | Configure Jira-GitHub Smart Commits Integration | Commits containing `ASDD-X` update Jira issue status. |

---

### 🎪 Epic 2: Core Machine Learning & Web Application (`ASDD-EPIC-2`)
*Objective:* Develop the Flask Eventopia portal interface, Gemini AI chatbot integration, and RandomForest ML intent classifier.

| Key | Issue Type | Summary | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| `ASDD-4` | Story | Develop Flask Eventopia Portal (`app.py`) | Application runs on port 5000 with UI and API endpoints. |
| `ASDD-5` | Story | Train & Persist Scikit-Learn ML Intent Classifier | Classifier accurately predicts intent from `intents.json`. |
| `ASDD-6` | Story | Design Modern Interactive UI & Event Portal | CSS stylesheet & HTML template render responsive interface. |

---

### ⚙️ Epic 3: Automated CI/CD Pipeline (`ASDD-EPIC-3`)
*Objective:* Automate checkout, build, unit testing, and container deployment using Jenkins.

| Key | Issue Type | Summary | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| `ASDD-7` | Story | Create Pytest Unit Test Suite (`test_app.py`) | Tests check `/`, `/health`, `/api/info`, `/predict`. |
| `ASDD-8` | Story | Author 5-Stage Declarative `Jenkinsfile` | Pipeline executes SCM, Build, Pytest, Docker Build, Deploy. |
| `ASDD-9` | Story | Setup GitHub Webhook Trigger | `git push` automatically fires Jenkins Pipeline build. |

---

### 🐳 Epic 4: Containerization & Server Configuration (`ASDD-EPIC-4`)
*Objective:* Package application into Docker containers and automate server setup with Ansible.

| Key | Issue Type | Summary | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| `ASDD-10` | Story | Create `Dockerfile` & `.dockerignore` | Multi-stage Docker image builds cleanly under 200MB. |
| `ASDD-11` | Story | Write Ansible Configuration Playbook (`deploy.yml`) | Playbook installs Docker, pulls code, runs container. |

---

### ☁️ Epic 5: Infrastructure as Code & AWS Deployment (`ASDD-EPIC-5`)
*Objective:* Provision cloud EC2 infrastructure via Terraform and verify production deployment.

| Key | Issue Type | Summary | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| `ASDD-12` | Story | Author Terraform IaC (`main.tf`, `outputs.tf`) | `terraform apply` provisions EC2 instance and returns IP. |
| `ASDD-13` | Story | Execute End-to-End AWS Production Deploy | Web application accessible live via `http://<EC2_PUBLIC_IP>:5000`. |

---

## 3. Sprint 1 Execution & Tracking
- **Sprint Name:** `ASDD Sprint 1 - Core DevOps Pipeline`
- **Total Story Points:** 24 Points
- **Sprint Goal:** Deliver working ML application deployed via automated Jenkins CI/CD pipeline on Docker & AWS.

### Workflow States:
1. `TO DO`: Backlog items awaiting sprint pickup.
2. `IN PROGRESS`: Active development on feature branch.
3. `IN REVIEW`: Code pushed to GitHub, Jenkins unit tests passing.
4. `DONE`: Merged to `main` branch and container deployed.

---

## 4. How to Perform Jira-GitHub Smart Commits Integration
When committing changes in Git, reference the Jira Issue Key in your commit message:

```bash
git commit -m "ASDD-4 Add Flask app routes and ML model initialization"
git commit -m "ASDD-8 Add Jenkinsfile declarative pipeline"
git commit -m "ASDD-10 ASDD-11 Add Dockerfile and Ansible playbook"
```

This links your code changes directly to the Jira board for automated traceability during practical verification and viva evaluation.
