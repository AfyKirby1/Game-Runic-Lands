# Git Commands Cheat Sheet

## Basic Commands

### Starting a New Repository
```bash
git init                    # Initialize a new Git repository
git clone <repository-url>  # Clone an existing repository
```

### Checking Status
```bash
git status                  # Check the status of your working directory
git log                     # View commit history
```

### Making Changes
```bash
git add .                   # Stage all changes
git add <filename>          # Stage specific file
git commit -m "message"     # Commit staged changes with a message
```

### Working with Remote Repositories
```bash
git push origin main        # Push changes to GitHub
git pull origin main        # Pull changes from GitHub
git fetch                   # Download changes from remote
```

### Branching
```bash
git branch                  # List all branches
git branch <name>           # Create a new branch
git checkout <branch>       # Switch to a branch
git merge <branch>          # Merge a branch into current branch
```

### Saving Work Temporarily
```bash
git stash                   # Save changes temporarily
git stash pop              # Apply saved changes back
```

### Fixing Mistakes
```bash
git reset --hard HEAD      # Discard all changes since last commit
git checkout -- <file>     # Discard changes to a specific file
```

## Common Workflow

1. Make changes to your files
2. `git add .` to stage changes
3. `git commit -m "your message"` to commit changes
4. `git push origin main` to push to GitHub

## Getting Help
```bash
git help <command>         # Get help for a specific command
git <command> --help       # Alternative way to get help
```

## Tips
- Always write meaningful commit messages
- Pull before pushing to avoid conflicts
- Use branches for new features
- Keep your .gitignore file updated 