# Guide: Setting Up GitHub on VS Code & Your First Fork

Welcome! This guide will walk you through the essential steps to connect **Visual Studio Code (VS Code)** to **GitHub** and teach you how to **fork** a project to start contributing.

---

## Step 1: Prerequisites
Before starting, ensure you have the following installed on your machine:

1. **VS Code:** [Download here](https://code.visualstudio.com/)
2. **Git:** [Download here](https://git-scm.com/downloads) (Required for VS Code to talk to GitHub).
3. **GitHub Account:** [Sign up here](https://github.com/)

---

## Step 2: Connect VS Code to GitHub
VS Code has built-in integration that makes managing your code easy without needing complex terminal commands.

1. Open **VS Code**.
2. Click on the **Accounts** icon (the person silhouette in the bottom-left corner).
3. Select **"Sign in with GitHub"**.
4. Your browser will open a GitHub authorization page. Click **Authorize Visual Studio Code**.
5. Once redirected back to VS Code, you are officially logged in!

---

## Step 3: Forking Your First Project
"Forking" is like taking a photocopy of someone else's project. It creates a copy under **your** account so you can make changes without affecting the original.

1. Go to the GitHub page of the project you want to copy.
2. In the top-right corner, click the **Fork** button.
3. Select your GitHub username as the owner.
4. **Wait a few seconds**—GitHub is now creating your personal copy of the repository.

---

##  Step 4: Cloning to Your Computer
Now that you have a "fork" on GitHub, you need to bring that code onto your actual computer.

1. On **your forked version** of the repo, click the green **<> Code** button.
2. Copy the **HTTPS** URL (it looks like `https://github.com/YourUsername/repository.git`).
3. Open **VS Code**.
4. Press `Ctrl + Shift + P` (Windows/Linux) or `Cmd + Shift + P` (Mac) to open the **Command Palette**.
5. Type `Git: Clone` and press **Enter**.
6. Paste the URL you copied and select a folder on your computer to save the project.
7. Click **Open** when the notification appears in the bottom right.

---
 
##  Step 5: Save & Upload Your Changes (OPTIONAL)
Once you've edited a file, you need to "Commit" (save a snapshot) and "Push" (upload to GitHub).

1. Click the **Source Control** icon on the left sidebar (looks like a branching tree).
2. You will see your modified files. Click the **+** (plus) icon next to a file to **Stage** it.
3. Type a descriptive **Commit Message** in the box (e.g., `"Added my first feature"`) and click **Commit**.
4. Click the **Sync Changes** button (or the blue "Push" button) to upload your work to GitHub.

---


### Need Help?
* [VS Code Official Git Doc](https://code.visualstudio.com/docs/sourcecontrol/intro-to-git)
* [GitHub Forking Guide](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
